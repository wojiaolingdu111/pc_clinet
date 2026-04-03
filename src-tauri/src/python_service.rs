use anyhow::{Context, Result};
use reqwest::Client;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServiceStatusResponse {
    pub running: bool,
    pub mode: String,
    pub base_url: String,
    pub message: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VoiceProfile {
    pub id: String,
    pub name: String,
    #[serde(rename = "type")]
    pub voice_type: String,
    pub language: Vec<String>,
    pub preview_audio: Option<String>,
    pub description: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VoicesResponse {
    pub builtin_voices: Vec<VoiceProfile>,
    pub custom_voices: Vec<VoiceProfile>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GenerateSpeechPayload {
    pub text: String,
    pub voice_id: String,
    pub speed: f32,
    pub language: String,
    pub output_format: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GenerateSpeechResponse {
    pub task_id: String,
    pub status: String,
    pub audio_path: Option<String>,
    pub error: Option<String>,
    pub duration_ms: Option<u128>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CloneVoicePayload {
    pub name: String,
    pub audio_path: String,
    pub language: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CloneVoiceResponse {
    pub voice_profile_id: String,
    pub status: String,
}

pub async fn get_service_status(
    client: &Client,
    base_url: &str,
    backend_token: Option<&str>,
) -> ServiceStatusResponse {
    let health_url = format!("{base_url}/health");

    match with_auth(client.get(&health_url), backend_token).send().await {
        Ok(response) if response.status().is_success() => ServiceStatusResponse {
            running: true,
            mode: "mock".to_string(),
            base_url: base_url.to_string(),
            message: "Python 本地服务可访问。".to_string(),
        },
        Ok(response) => ServiceStatusResponse {
            running: false,
            mode: "offline".to_string(),
            base_url: base_url.to_string(),
            message: format!("Python 服务响应异常：{}", response.status()),
        },
        Err(_) => ServiceStatusResponse {
            running: false,
            mode: "offline".to_string(),
            base_url: base_url.to_string(),
            message: "Python 服务未启动，请先运行 python-backend/app.py。".to_string(),
        },
    }
}

fn with_auth(builder: reqwest::RequestBuilder, backend_token: Option<&str>) -> reqwest::RequestBuilder {
    if let Some(token) = backend_token {
        builder.header("x-aitoreder-token", token)
    } else {
        builder
    }
}

pub async fn list_voices(
    client: &Client,
    base_url: &str,
    backend_token: Option<&str>,
) -> Result<VoicesResponse> {
    let url = format!("{base_url}/voices");
    let response = with_auth(client.get(url), backend_token)
        .send()
        .await
        .context("无法连接 Python 服务")?
        .error_for_status()
        .context("Python 服务返回了错误状态")?;

    response
        .json::<VoicesResponse>()
        .await
        .context("音色列表解析失败")
}

pub async fn generate_speech(
    client: &Client,
    base_url: &str,
    backend_token: Option<&str>,
    payload: &GenerateSpeechPayload,
) -> Result<GenerateSpeechResponse> {
    let url = format!("{base_url}/generate-speech");
    let response = with_auth(client.post(url), backend_token)
        .json(payload)
        .send()
        .await
        .context("调用 Python 生成接口失败")?
        .error_for_status()
        .context("Python 生成接口返回错误")?;

    response
        .json::<GenerateSpeechResponse>()
        .await
        .context("生成结果解析失败")
}

pub async fn clone_voice(
    client: &Client,
    base_url: &str,
    backend_token: Option<&str>,
    payload: &CloneVoicePayload,
) -> Result<CloneVoiceResponse> {
    let url = format!("{base_url}/clone-voice");
    let response = with_auth(client.post(url), backend_token)
        .json(payload)
        .send()
        .await
        .context("调用声音克隆接口失败")?
        .error_for_status()
        .context("声音克隆接口返回错误")?;

    response
        .json::<CloneVoiceResponse>()
        .await
        .context("声音克隆结果解析失败")
}

pub async fn delete_voice_profile(
    client: &Client,
    base_url: &str,
    backend_token: Option<&str>,
    voice_profile_id: &str,
) -> Result<()> {
    let url = format!("{base_url}/voices/{voice_profile_id}");
    with_auth(client.delete(url), backend_token)
        .send()
        .await
        .context("删除音色 profile 失败")?
        .error_for_status()
        .context("删除音色 profile 返回错误")?;

    Ok(())
}
