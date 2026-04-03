use anyhow::Result;
use std::fs;
use std::path::PathBuf;

#[derive(Clone)]
pub struct AppDirectories {
    pub root: PathBuf,
    pub outputs: PathBuf,
    pub voices: PathBuf,
    pub models: PathBuf,
    pub logs: PathBuf,
}

impl AppDirectories {
    pub fn new(root: PathBuf) -> Result<Self> {
        let outputs = root.join("outputs");
        let voices = root.join("voices");
        let models = root.join("models");
        let logs = root.join("logs");

        for dir in [&root, &outputs, &voices, &models, &logs] {
            fs::create_dir_all(dir)?;
        }

        Ok(Self {
            root,
            outputs,
            voices,
            models,
            logs,
        })
    }
}
