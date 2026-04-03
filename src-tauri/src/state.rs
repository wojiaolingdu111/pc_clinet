use anyhow::Result;
use reqwest::Client;
use std::path::PathBuf;
use tauri::{AppHandle, Manager};

use crate::file_manager::AppDirectories;

pub struct AppState {
    pub directories: AppDirectories,
    pub client: Client,
    pub python_base_url: String,
}

impl AppState {
    pub fn new(app_handle: &AppHandle) -> Result<Self> {
        let app_data_dir = app_handle
            .path()
            .app_data_dir()
            .unwrap_or_else(|| PathBuf::from("app-data"));
        let directories = AppDirectories::new(app_data_dir)?;

        Ok(Self {
            directories,
            client: Client::new(),
            python_base_url: "http://127.0.0.1:8765".to_string(),
        })
    }
}
