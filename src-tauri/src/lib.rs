pub mod commands;
pub mod engine;
pub mod global_hook;

use commands::AppState;
use engine::DictionaryEngine;
use std::sync::RwLock;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let engine = DictionaryEngine::new();

    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .manage(AppState {
            engine: RwLock::new(engine),
        })
        .setup(|app| {
            global_hook::init_global_hook(app.handle().clone());
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::search,
            commands::mark_used,
            commands::reset_used,
            commands::get_engine_stats,
            commands::load_custom_wordlist,
            commands::restore_default_wordlist,
            commands::set_background_tracking,
        ])
        .run(tauri::generate_context!())
        .expect("error while running Affixr application");
}
