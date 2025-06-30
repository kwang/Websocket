package com.interview.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

import java.nio.file.Path;
import java.nio.file.Paths;

@Configuration
@ConfigurationProperties(prefix = "interview")
public class InterviewConfig {
    
    // Recording settings
    private Path recordingsDir = Paths.get("recordings");
    private int maxRecordingSizeMb = 50;
    private String audioFormat = "mp3";
    private String audioQuality = "high";
    
    // Session settings
    private int sessionTimeoutMinutes = 60;
    private int autoCleanupDays = 30;
    
    // Whisper settings
    private String whisperModel = "base";
    
    // Server settings
    private String host = "0.0.0.0";
    private int port = 9090; // gRPC default port
    private boolean debug = true;
    
    // Metadata settings
    private boolean saveTranscription = true;
    private boolean saveAudioDuration = true;
    private boolean saveAudioQuality = true;
    
    // File naming patterns
    private String audioFilenamePattern = "response_{timestamp}.{ext}";
    private String metadataFilenamePattern = "metadata_{timestamp}.json";
    private String sessionIdPattern = "interview_{date}_{time}_{client_suffix}";
    
    // Combined audio settings
    private boolean createCombinedAudio = false;
    private String combinedAudioFilename = "combined_interview.mp3";
    
    // Backup settings
    private boolean autoBackup = false;
    private Path backupDir = Paths.get("backups");
    private int backupIntervalHours = 24;
    
    // Security settings
    private String allowedOrigins = "*";
    private boolean requireAuthentication = false;
    private String apiKey = null;
    
    // OpenAI settings
    private String openaiApiKey = "your-openai-api-key-here";
    private String openaiModel = "gpt-3.5-turbo";
    private int openaiMaxTokens = 150;
    private double openaiTemperature = 0.7;
    private boolean useOpenaiForInterview = true;
    
    // OpenAI TTS settings
    private boolean useOpenaiTts = true;
    private String openaiTtsVoice = "alloy";
    private String openaiTtsModel = "tts-1";
    
    // gRPC settings
    private int grpcPort = 9090;
    private int maxMessageSize = 50 * 1024 * 1024; // 50MB
    
    // Getters and Setters
    public Path getRecordingsDir() { return recordingsDir; }
    public void setRecordingsDir(Path recordingsDir) { this.recordingsDir = recordingsDir; }
    
    public int getMaxRecordingSizeMb() { return maxRecordingSizeMb; }
    public void setMaxRecordingSizeMb(int maxRecordingSizeMb) { this.maxRecordingSizeMb = maxRecordingSizeMb; }
    
    public String getAudioFormat() { return audioFormat; }
    public void setAudioFormat(String audioFormat) { this.audioFormat = audioFormat; }
    
    public String getAudioQuality() { return audioQuality; }
    public void setAudioQuality(String audioQuality) { this.audioQuality = audioQuality; }
    
    public int getSessionTimeoutMinutes() { return sessionTimeoutMinutes; }
    public void setSessionTimeoutMinutes(int sessionTimeoutMinutes) { this.sessionTimeoutMinutes = sessionTimeoutMinutes; }
    
    public int getAutoCleanupDays() { return autoCleanupDays; }
    public void setAutoCleanupDays(int autoCleanupDays) { this.autoCleanupDays = autoCleanupDays; }
    
    public String getWhisperModel() { return whisperModel; }
    public void setWhisperModel(String whisperModel) { this.whisperModel = whisperModel; }
    
    public String getHost() { return host; }
    public void setHost(String host) { this.host = host; }
    
    public int getPort() { return port; }
    public void setPort(int port) { this.port = port; }
    
    public boolean isDebug() { return debug; }
    public void setDebug(boolean debug) { this.debug = debug; }
    
    public boolean isSaveTranscription() { return saveTranscription; }
    public void setSaveTranscription(boolean saveTranscription) { this.saveTranscription = saveTranscription; }
    
    public boolean isSaveAudioDuration() { return saveAudioDuration; }
    public void setSaveAudioDuration(boolean saveAudioDuration) { this.saveAudioDuration = saveAudioDuration; }
    
    public boolean isSaveAudioQuality() { return saveAudioQuality; }
    public void setSaveAudioQuality(boolean saveAudioQuality) { this.saveAudioQuality = saveAudioQuality; }
    
    public String getAudioFilenamePattern() { return audioFilenamePattern; }
    public void setAudioFilenamePattern(String audioFilenamePattern) { this.audioFilenamePattern = audioFilenamePattern; }
    
    public String getMetadataFilenamePattern() { return metadataFilenamePattern; }
    public void setMetadataFilenamePattern(String metadataFilenamePattern) { this.metadataFilenamePattern = metadataFilenamePattern; }
    
    public String getSessionIdPattern() { return sessionIdPattern; }
    public void setSessionIdPattern(String sessionIdPattern) { this.sessionIdPattern = sessionIdPattern; }
    
    public boolean isCreateCombinedAudio() { return createCombinedAudio; }
    public void setCreateCombinedAudio(boolean createCombinedAudio) { this.createCombinedAudio = createCombinedAudio; }
    
    public String getCombinedAudioFilename() { return combinedAudioFilename; }
    public void setCombinedAudioFilename(String combinedAudioFilename) { this.combinedAudioFilename = combinedAudioFilename; }
    
    public boolean isAutoBackup() { return autoBackup; }
    public void setAutoBackup(boolean autoBackup) { this.autoBackup = autoBackup; }
    
    public Path getBackupDir() { return backupDir; }
    public void setBackupDir(Path backupDir) { this.backupDir = backupDir; }
    
    public int getBackupIntervalHours() { return backupIntervalHours; }
    public void setBackupIntervalHours(int backupIntervalHours) { this.backupIntervalHours = backupIntervalHours; }
    
    public String getAllowedOrigins() { return allowedOrigins; }
    public void setAllowedOrigins(String allowedOrigins) { this.allowedOrigins = allowedOrigins; }
    
    public boolean isRequireAuthentication() { return requireAuthentication; }
    public void setRequireAuthentication(boolean requireAuthentication) { this.requireAuthentication = requireAuthentication; }
    
    public String getApiKey() { return apiKey; }
    public void setApiKey(String apiKey) { this.apiKey = apiKey; }
    
    public String getOpenaiApiKey() { return openaiApiKey; }
    public void setOpenaiApiKey(String openaiApiKey) { this.openaiApiKey = openaiApiKey; }
    
    public String getOpenaiModel() { return openaiModel; }
    public void setOpenaiModel(String openaiModel) { this.openaiModel = openaiModel; }
    
    public int getOpenaiMaxTokens() { return openaiMaxTokens; }
    public void setOpenaiMaxTokens(int openaiMaxTokens) { this.openaiMaxTokens = openaiMaxTokens; }
    
    public double getOpenaiTemperature() { return openaiTemperature; }
    public void setOpenaiTemperature(double openaiTemperature) { this.openaiTemperature = openaiTemperature; }
    
    public boolean isUseOpenaiForInterview() { return useOpenaiForInterview; }
    public void setUseOpenaiForInterview(boolean useOpenaiForInterview) { this.useOpenaiForInterview = useOpenaiForInterview; }
    
    public boolean isUseOpenaiTts() { return useOpenaiTts; }
    public void setUseOpenaiTts(boolean useOpenaiTts) { this.useOpenaiTts = useOpenaiTts; }
    
    public String getOpenaiTtsVoice() { return openaiTtsVoice; }
    public void setOpenaiTtsVoice(String openaiTtsVoice) { this.openaiTtsVoice = openaiTtsVoice; }
    
    public String getOpenaiTtsModel() { return openaiTtsModel; }
    public void setOpenaiTtsModel(String openaiTtsModel) { this.openaiTtsModel = openaiTtsModel; }
    
    public int getGrpcPort() { return grpcPort; }
    public void setGrpcPort(int grpcPort) { this.grpcPort = grpcPort; }
    
    public int getMaxMessageSize() { return maxMessageSize; }
    public void setMaxMessageSize(int maxMessageSize) { this.maxMessageSize = maxMessageSize; }
} 