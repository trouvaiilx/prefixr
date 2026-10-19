use crate::engine::{DictionaryEngine, EngineStats, SearchMode, SearchResponse, SortOrder};
use crate::global_hook;
use std::path::Path;
use std::sync::RwLock;
use tauri::State;

pub struct AppState {
    pub engine: RwLock<DictionaryEngine>,
}

#[tauri::command]
pub fn search(
    state: State<'_, AppState>,
    query: String,
    mode: SearchMode,
    sort_order: SortOrder,
    max_results: usize,
    bg_tracking_enabled: bool,
) -> Result<SearchResponse, String> {
    let trimmed = query.trim();
    global_hook::set_hook_active(bg_tracking_enabled && !trimmed.is_empty());

    let engine = state
        .engine
        .read()
        .map_err(|_| "Failed to acquire read lock on dictionary engine".to_string())?;

    Ok(engine.search(trimmed, mode, sort_order, max_results))
}

#[tauri::command]
pub fn mark_used(state: State<'_, AppState>, word: String) -> Result<EngineStats, String> {
    let mut engine = state
        .engine
        .write()
        .map_err(|_| "Failed to acquire write lock on dictionary engine".to_string())?;

    Ok(engine.mark_used(&word))
}

#[tauri::command]
pub fn reset_used(state: State<'_, AppState>) -> Result<EngineStats, String> {
    let mut engine = state
        .engine
        .write()
        .map_err(|_| "Failed to acquire write lock on dictionary engine".to_string())?;

    Ok(engine.reset_used())
}

#[tauri::command]
pub fn get_engine_stats(state: State<'_, AppState>) -> Result<EngineStats, String> {
    let engine = state
        .engine
        .read()
        .map_err(|_| "Failed to acquire read lock on dictionary engine".to_string())?;

    Ok(engine.stats())
}

#[tauri::command]
pub fn load_custom_wordlist(
    state: State<'_, AppState>,
    path: String,
) -> Result<EngineStats, String> {
    let mut engine = state
        .engine
        .write()
        .map_err(|_| "Failed to acquire write lock on dictionary engine".to_string())?;

    engine.load_from_file(Path::new(&path))
}

#[tauri::command]
pub fn restore_default_wordlist(state: State<'_, AppState>) -> Result<EngineStats, String> {
    let mut engine = state
        .engine
        .write()
        .map_err(|_| "Failed to acquire write lock on dictionary engine".to_string())?;

    engine.load_default();
    Ok(engine.stats())
}

#[tauri::command]
pub fn set_background_tracking(enabled: bool, has_query: bool) -> Result<(), String> {
    global_hook::set_hook_active(enabled && has_query);
    Ok(())
}
