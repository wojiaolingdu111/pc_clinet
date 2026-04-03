use anyhow::Result;
use rand::{distributions::Alphanumeric, Rng};
use reqwest::Client;
use std::env;
use std::net::{SocketAddr, TcpListener, TcpStream};
use std::path::Path;
use std::process::Command;
use std::thread;
use std::time::Duration;
use std::path::PathBuf;
use tauri::{AppHandle, Manager};

use crate::file_manager::AppDirectories;

pub struct AppState {
    pub directories: AppDirectories,
    pub client: Client,
    pub python_base_url: String,
    pub backend_token: Option<String>,
}

impl AppState {
    pub fn new(app_handle: &AppHandle) -> Result<Self> {
        let app_data_dir = app_handle
            .path()
            .app_data_dir()
            .unwrap_or_else(|| PathBuf::from("app-data"));
        let directories = AppDirectories::new(app_data_dir)?;

        let startup = ensure_python_backend_running(app_handle);

        Ok(Self {
            directories,
            client: Client::new(),
            python_base_url: startup.base_url,
            backend_token: startup.token,
        })
    }
}

struct BackendStartup {
    base_url: String,
    token: Option<String>,
}

fn ensure_python_backend_running(app_handle: &AppHandle) -> BackendStartup {
    let default_url = "http://127.0.0.1:8765".to_string();
    let default_addr: SocketAddr = match "127.0.0.1:8765".parse() {
        Ok(value) => value,
        Err(_) => {
            return BackendStartup {
                base_url: default_url,
                token: None,
            }
        }
    };

    if TcpStream::connect_timeout(&default_addr, Duration::from_millis(350)).is_ok() {
        return BackendStartup {
            base_url: default_url,
            token: None,
        };
    }

    let port = match pick_available_port() {
        Some(value) => value,
        None => {
            return BackendStartup {
                base_url: default_url,
                token: None,
            }
        }
    };

    let token = generate_token();
    let addr: SocketAddr = match format!("127.0.0.1:{port}").parse() {
        Ok(value) => value,
        Err(_) => {
            return BackendStartup {
                base_url: default_url,
                token: None,
            }
        }
    };

    let backend_dir = match find_backend_dir(app_handle) {
        Some(path) => path,
        None => {
            eprintln!("python-backend 目录未找到，跳过自动启动。\n");
            return BackendStartup {
                base_url: default_url,
                token: None,
            };
        }
    };

    let launchers = [
        ("python", Vec::<String>::new()),
        ("python3", Vec::<String>::new()),
        ("py", vec!["-3".to_string()]),
    ];

    for (bin, mut prefix_args) in launchers {
        let mut command = Command::new(bin);
        command.current_dir(&backend_dir);
        command.env("AITOREDER_BACKEND_PORT", port.to_string());
        command.env("AITOREDER_BACKEND_TOKEN", token.as_str());
        prefix_args.push("app.py".to_string());
        command.args(prefix_args);

        if command.spawn().is_ok() {
            if wait_for_port(addr) {
                eprintln!("已自动启动 Python 后端：{}", bin);
                return BackendStartup {
                    base_url: format!("http://127.0.0.1:{port}"),
                    token: Some(token),
                };
            }

            break;
        }
    }

    eprintln!("自动启动 Python 后端失败，请手动运行 python-backend/app.py。");
    BackendStartup {
        base_url: default_url,
        token: None,
    }
}

fn pick_available_port() -> Option<u16> {
    let listener = TcpListener::bind("127.0.0.1:0").ok()?;
    listener.local_addr().ok().map(|addr| addr.port())
}

fn generate_token() -> String {
    rand::thread_rng()
        .sample_iter(&Alphanumeric)
        .take(40)
        .map(char::from)
        .collect()
}

fn wait_for_port(addr: SocketAddr) -> bool {
    for _ in 0..25 {
        if TcpStream::connect_timeout(&addr, Duration::from_millis(250)).is_ok() {
            return true;
        }

        thread::sleep(Duration::from_millis(180));
    }

    false
}

fn find_backend_dir(app_handle: &AppHandle) -> Option<PathBuf> {
    let mut candidates: Vec<PathBuf> = Vec::new();

    if let Ok(cwd) = env::current_dir() {
        candidates.push(cwd.join("python-backend"));
        candidates.push(cwd.join("..").join("python-backend"));
    }

    if let Ok(resource_dir) = app_handle.path().resource_dir() {
        candidates.push(resource_dir.join("python-backend"));
    }

    if let Ok(exe_path) = env::current_exe() {
        if let Some(exe_dir) = exe_path.parent() {
            candidates.push(exe_dir.join("python-backend"));
            candidates.push(exe_dir.join("resources").join("python-backend"));
        }
    }

    candidates
        .into_iter()
        .find(|path| is_backend_dir(path.as_path()))
}

fn is_backend_dir(path: &Path) -> bool {
    path.join("app.py").exists() && path.join("requirements.txt").exists()
}
