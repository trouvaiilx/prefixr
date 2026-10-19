use serde::Serialize;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::mpsc::{self, SyncSender};
use std::sync::OnceLock;
use tauri::{AppHandle, Emitter, Manager};

static HOOK_ACTIVE: AtomicBool = AtomicBool::new(false);
static KEY_SENDER: OnceLock<SyncSender<GlobalKeyPayload>> = OnceLock::new();

#[derive(Debug, Clone, Serialize)]
#[serde(tag = "kind", content = "value", rename_all = "lowercase")]
pub enum GlobalKeyPayload {
    Char(char),
    Backspace,
    Enter,
}

pub fn set_hook_active(active: bool) {
    HOOK_ACTIVE.store(active, Ordering::Relaxed);
}

pub fn init_global_hook(app_handle: AppHandle) {
    let (tx, rx) = mpsc::sync_channel::<GlobalKeyPayload>(64);
    let _ = KEY_SENDER.set(tx);

    // Dispatcher thread: forwards events to webview only when window is unfocused
    std::thread::spawn(move || {
        while let Ok(payload) = rx.recv() {
            if !HOOK_ACTIVE.load(Ordering::Relaxed) {
                continue;
            }
            let is_focused = app_handle
                .get_webview_window("main")
                .and_then(|w| w.is_focused().ok())
                .unwrap_or(false);

            if !is_focused {
                let _ = app_handle.emit("affixr://global-key", payload);
            }
        }
    });

    #[cfg(windows)]
    std::thread::spawn(|| {
        windows_hook::run_hook_loop();
    });
}

#[cfg(windows)]
mod windows_hook {
    use super::{GlobalKeyPayload, HOOK_ACTIVE, KEY_SENDER};
    use std::sync::atomic::Ordering;
    use windows_sys::Win32::Foundation::{LPARAM, LRESULT, WPARAM};
    use windows_sys::Win32::UI::Input::KeyboardAndMouse::{
        GetAsyncKeyState, VK_BACK, VK_CONTROL, VK_LWIN, VK_MENU, VK_RETURN, VK_RWIN,
    };
    use windows_sys::Win32::UI::WindowsAndMessaging::{
        CallNextHookEx, GetMessageW, SetWindowsHookExW, UnhookWindowsHookEx, HC_ACTION,
        KBDLLHOOKSTRUCT, MSG, WH_KEYBOARD_LL, WM_KEYDOWN, WM_SYSKEYDOWN,
    };

    unsafe extern "system" fn low_level_keyboard_proc(
        n_code: i32,
        w_param: WPARAM,
        l_param: LPARAM,
    ) -> LRESULT {
        if n_code == HC_ACTION as i32
            && HOOK_ACTIVE.load(Ordering::Relaxed)
            && (w_param == WM_KEYDOWN as WPARAM || w_param == WM_SYSKEYDOWN as WPARAM)
        {
            let kb = &*(l_param as *const KBDLLHOOKSTRUCT);
            let vk = kb.vkCode as u16;

            if let Some(tx) = KEY_SENDER.get() {
                if (0x41..=0x5A).contains(&vk) {
                    let ctrl = GetAsyncKeyState(VK_CONTROL as i32) < 0;
                    let alt = GetAsyncKeyState(VK_MENU as i32) < 0;
                    let lwin = GetAsyncKeyState(VK_LWIN as i32) < 0;
                    let rwin = GetAsyncKeyState(VK_RWIN as i32) < 0;

                    if !ctrl && !alt && !lwin && !rwin {
                        let ch = (vk as u8 - b'A' + b'a') as char;
                        let _ = tx.try_send(GlobalKeyPayload::Char(ch));
                    }
                } else if vk == VK_BACK {
                    let _ = tx.try_send(GlobalKeyPayload::Backspace);
                } else if vk == VK_RETURN {
                    let _ = tx.try_send(GlobalKeyPayload::Enter);
                }
            }
        }

        CallNextHookEx(std::mem::zeroed(), n_code, w_param, l_param)
    }

    pub fn run_hook_loop() {
        unsafe {
            let hook = SetWindowsHookExW(
                WH_KEYBOARD_LL,
                Some(low_level_keyboard_proc),
                std::mem::zeroed(),
                0,
            );
            if hook.is_null() {
                return;
            }

            let mut msg: MSG = std::mem::zeroed();
            while GetMessageW(&mut msg, std::mem::zeroed(), 0, 0) > 0 {}

            UnhookWindowsHookEx(hook);
        }
    }
}
