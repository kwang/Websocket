package com.interview.service;

import com.interview.config.InterviewConfig;
import com.interview.grpc.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import java.util.Base64;

// HTTP client imports for OpenAI API
import okhttp3.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.BufferedWriter;
import java.nio.file.StandardCopyOption;

@Service
public class InterviewServiceImpl implements InterviewService {
    
    private static final Logger logger = LoggerFactory.getLogger(InterviewServiceImpl.class);
    
    @Autowired
    private InterviewConfig config;
    
    @Override
    public StartInterviewResponse startInterview(StartInterviewRequest request) {
        try {
            // Generate a unique session ID
            String sessionId = generateSessionId(request.getClientId());
            
            // Create session directory
            Path sessionDir = config.getRecordingsDir().resolve(sessionId);
            Files.createDirectories(sessionDir);
            
            String greetingMessage = "Hello! I'm your AI interviewer today. Let's begin with your introduction. Could you please tell me about yourself?";
            
            logger.info("Started interview session: {} for client: {}", sessionId, request.getClientId());
            
            return StartInterviewResponse.newBuilder()
                    .setSuccess(true)
                    .setSessionId(sessionId)
                    .setGreetingMessage(greetingMessage)
                    .build();
                    
        } catch (Exception e) {
            logger.error("Error starting interview", e);
            return StartInterviewResponse.newBuilder()
                    .setSuccess(false)
                    .setErrorMessage("Failed to start interview: " + e.getMessage())
                    .build();
        }
    }
    
    @Override
    public ProcessAudioResponse processAudio(ProcessAudioRequest request) {
        try {
            String sessionId = request.getSessionId();
            byte[] audioData = request.getAudioData().toByteArray();
            String audioFormat = request.getAudioFormat();
            
            // Determine file extension based on audio format
            String fileExtension = "webm"; // default
            if (audioFormat != null) {
                switch (audioFormat.toLowerCase()) {
                    case "mp4":
                        fileExtension = "mp4";
                        break;
                    case "wav":
                        fileExtension = "wav";
                        break;
                    case "mp3":
                        fileExtension = "mp3";
                        break;
                    case "webm":
                    default:
                        fileExtension = "webm";
                        break;
                }
            }
            
            // Save audio file with correct extension
            String audioFileName = "response_" + System.currentTimeMillis() + "." + fileExtension;
            Path audioPath = config.getRecordingsDir().resolve(sessionId).resolve(audioFileName);
            Files.write(audioPath, audioData);
            
            // For now, return a dummy transcription
            // In a real implementation, this would use Whisper or another speech-to-text service
            String transcription = "This is a sample transcription of the audio response.";
            
            // Generate a follow-up question
            String followUpQuestion = generateFollowUpQuestion(transcription);
            
            logger.info("Processed audio for session: {}, saved to: {}", sessionId, audioPath);
            
            return ProcessAudioResponse.newBuilder()
                    .setSuccess(true)
                    .setTranscription(transcription)
                    .setFollowUpQuestion(followUpQuestion)
                    .setAudioFilePath(audioPath.toString())
                    .build();
                    
        } catch (Exception e) {
            logger.error("Error processing audio", e);
            return ProcessAudioResponse.newBuilder()
                    .setSuccess(false)
                    .setErrorMessage("Failed to process audio: " + e.getMessage())
                    .build();
        }
    }
    
    @Override
    public GenerateSpeechResponse generateSpeech(GenerateSpeechRequest request) {
        try {
            String text = request.getText();
            String voice = request.getVoice();
            String sessionId = request.getSessionId();
            
            // Use OpenAI TTS to generate real speech
            byte[] audioData = generateOpenAITTS(text, voice);
            
            // Save the generated speech
            String speechFileName = "speech_" + System.currentTimeMillis() + ".mp3";
            Path speechPath = config.getRecordingsDir().resolve(sessionId).resolve(speechFileName);
            Files.write(speechPath, audioData);
            
            logger.info("Generated speech for session: {}, saved to: {}", sessionId, speechPath);
            
            return GenerateSpeechResponse.newBuilder()
                    .setSuccess(true)
                    .setAudioData(com.google.protobuf.ByteString.copyFrom(audioData))
                    .setAudioFilePath(speechPath.toString())
                    .build();
                    
        } catch (Exception e) {
            logger.error("Error generating speech", e);
            return GenerateSpeechResponse.newBuilder()
                    .setSuccess(false)
                    .setErrorMessage("Failed to generate speech: " + e.getMessage())
                    .build();
        }
    }
    
    @Override
    public FinishInterviewResponse finishInterview(FinishInterviewRequest request) {
        try {
            String sessionId = request.getSessionId();

            // Mix TTS audio with user video
            boolean mixed = mixTTSWithUserVideo(sessionId);

            logger.info("Finished interview session: {}. Mixed video: {}", sessionId, mixed);

            return FinishInterviewResponse.newBuilder()
                    .setSuccess(true)
                    .setAudioCombined(true)
                    .setVideoCombined(mixed)
                    .build();

        } catch (Exception e) {
            logger.error("Error finishing interview", e);
            return FinishInterviewResponse.newBuilder()
                    .setSuccess(false)
                    .setErrorMessage("Failed to finish interview: " + e.getMessage())
                    .build();
        }
    }
    
    @Override
    public GetQuestionsResponse getInterviewQuestions(GetQuestionsRequest request) {
        try {
            String category = request.getCategory();
            List<String> questions = generateQuestionsForCategory(category);
            
            return GetQuestionsResponse.newBuilder()
                    .addAllQuestions(questions)
                    .build();
                    
        } catch (Exception e) {
            logger.error("Error getting questions", e);
            return GetQuestionsResponse.newBuilder().build();
        }
    }
    
    @Override
    public InterviewMessage processStreamMessage(InterviewMessage message) {
        try {
            String text = message.getText();
            String response = "I heard you say: " + text + ". Please continue.";
            
            return InterviewMessage.newBuilder()
                    .setText(response)
                    .setMessageType(MessageType.QUESTION)
                    .build();
                    
        } catch (Exception e) {
            logger.error("Error processing stream message", e);
            return InterviewMessage.newBuilder()
                    .setText("Sorry, I didn't catch that. Could you repeat?")
                    .setMessageType(MessageType.QUESTION)
                    .build();
        }
    }
    
    // Helper methods
    
    private String generateSessionId(String clientId) {
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        String randomSuffix = UUID.randomUUID().toString().substring(0, 8);
        return "interview_" + timestamp + "_" + randomSuffix;
    }
    
    private String generateFollowUpQuestion(String transcription) {
        // Simple follow-up logic - in a real implementation, this would use AI
        List<String> followUps = Arrays.asList(
            "That's interesting! Could you elaborate on that?",
            "Thank you for sharing that. What was the outcome?",
            "How did you handle challenges in that situation?",
            "What did you learn from that experience?",
            "Can you give me a specific example?"
        );
        
        int index = (int) (System.currentTimeMillis() % followUps.size());
        return followUps.get(index);
    }
    
    private List<String> generateQuestionsForCategory(String category) {
        switch (category.toLowerCase()) {
            case "interview_start":
                return Arrays.asList(
                    "Hello! I'm your AI interviewer today. Could you please introduce yourself?",
                    "Could you tell me about your relevant experience?",
                    "What are your key technical skills?"
                );
            case "follow_up":
                return Arrays.asList(
                    "That's interesting! Could you elaborate on that?",
                    "Thank you for sharing that. What was the outcome?",
                    "How did you handle challenges in that situation?"
                );
            default:
                return Arrays.asList(
                    "Tell me about yourself.",
                    "What are your strengths?",
                    "Where do you see yourself in 5 years?"
                );
        }
    }
    
    private byte[] generateOpenAITTS(String text, String voice) {
        try {
            // Get OpenAI API key from config
            String apiKey = config.getOpenaiApiKey();
            if (apiKey == null || apiKey.trim().isEmpty()) {
                logger.error("OpenAI API key not configured");
                return generateFallbackAudio(text);
            }
            
            // Use default voice if not specified
            String selectedVoice = (voice != null && !voice.trim().isEmpty()) ? voice : "alloy";
            
            // Create HTTP client
            OkHttpClient client = new OkHttpClient();
            
            // Prepare request body
            String requestBody = String.format(
                "{\"model\":\"tts-1\",\"input\":\"%s\",\"voice\":\"%s\"}",
                text.replace("\"", "\\\""), // Escape quotes
                selectedVoice
            );
            
            // Create request
            Request request = new Request.Builder()
                .url("https://api.openai.com/v1/audio/speech")
                .addHeader("Authorization", "Bearer " + apiKey)
                .addHeader("Content-Type", "application/json")
                .post(RequestBody.create(requestBody, MediaType.get("application/json")))
                .build();
            
            // Execute request
            try (Response response = client.newCall(request).execute()) {
                if (!response.isSuccessful()) {
                    logger.error("OpenAI TTS API error: {} - {}", response.code(), response.body() != null ? response.body().string() : "No body");
                    return generateFallbackAudio(text);
                }
                
                // Get audio data
                ResponseBody body = response.body();
                if (body == null) {
                    logger.error("OpenAI TTS API returned empty response");
                    return generateFallbackAudio(text);
                }
                
                byte[] audioData = body.bytes();
                logger.info("Successfully generated TTS audio for text: '{}' with voice: {}", text, selectedVoice);
                return audioData;
                
            }
            
        } catch (Exception e) {
            logger.error("Error calling OpenAI TTS API", e);
            return generateFallbackAudio(text);
        }
    }
    
    private byte[] generateFallbackAudio(String text) {
        // Generate a simple fallback audio when OpenAI TTS fails
        logger.warn("Using fallback audio generation for text: {}", text);
        
        int sampleRate = 22050;
        int durationMs = Math.max(500, Math.min(2000, text.length() * 50));
        int numSamples = (sampleRate * durationMs) / 1000;
        int dataSize = numSamples * 2;
        int fileSize = 36 + dataSize;
        
        byte[] wavFile = new byte[44 + dataSize];
        int offset = 0;
        
        // RIFF header
        wavFile[offset++] = 'R'; wavFile[offset++] = 'I'; wavFile[offset++] = 'F'; wavFile[offset++] = 'F';
        wavFile[offset++] = (byte) (fileSize & 0xFF);
        wavFile[offset++] = (byte) ((fileSize >> 8) & 0xFF);
        wavFile[offset++] = (byte) ((fileSize >> 16) & 0xFF);
        wavFile[offset++] = (byte) ((fileSize >> 24) & 0xFF);
        wavFile[offset++] = 'W'; wavFile[offset++] = 'A'; wavFile[offset++] = 'V'; wavFile[offset++] = 'E';
        
        // fmt chunk
        wavFile[offset++] = 'f'; wavFile[offset++] = 'm'; wavFile[offset++] = 't'; wavFile[offset++] = ' ';
        wavFile[offset++] = 16; wavFile[offset++] = 0; wavFile[offset++] = 0; wavFile[offset++] = 0;
        wavFile[offset++] = 1; wavFile[offset++] = 0; // PCM format
        wavFile[offset++] = 1; wavFile[offset++] = 0; // mono
        wavFile[offset++] = (byte) (sampleRate & 0xFF);
        wavFile[offset++] = (byte) ((sampleRate >> 8) & 0xFF);
        wavFile[offset++] = (byte) ((sampleRate >> 16) & 0xFF);
        wavFile[offset++] = (byte) ((sampleRate >> 24) & 0xFF);
        int byteRate = sampleRate * 2;
        wavFile[offset++] = (byte) (byteRate & 0xFF);
        wavFile[offset++] = (byte) ((byteRate >> 8) & 0xFF);
        wavFile[offset++] = (byte) ((byteRate >> 16) & 0xFF);
        wavFile[offset++] = (byte) ((byteRate >> 24) & 0xFF);
        wavFile[offset++] = 2; wavFile[offset++] = 0; // block align
        wavFile[offset++] = 16; wavFile[offset++] = 0; // bits per sample
        
        // data chunk header
        wavFile[offset++] = 'd'; wavFile[offset++] = 'a'; wavFile[offset++] = 't'; wavFile[offset++] = 'a';
        wavFile[offset++] = (byte) (dataSize & 0xFF);
        wavFile[offset++] = (byte) ((dataSize >> 8) & 0xFF);
        wavFile[offset++] = (byte) ((dataSize >> 16) & 0xFF);
        wavFile[offset++] = (byte) ((dataSize >> 24) & 0xFF);
        
        // Generate audio samples - simple sine wave
        double frequency = 440.0;
        double amplitude = 0.3;
        
        for (int i = 0; i < numSamples; i++) {
            double sample = Math.sin(2 * Math.PI * frequency * i / sampleRate);
            short value = (short) (sample * 32767 * amplitude);
            
            wavFile[offset++] = (byte) (value & 0xFF);
            wavFile[offset++] = (byte) ((value >> 8) & 0xFF);
        }
        
        return wavFile;
    }

    // Helper to mix TTS audio with user video using ffmpeg
    private boolean mixTTSWithUserVideo(String sessionId) {
        try {
            Path sessionDir = config.getRecordingsDir().resolve(sessionId);
            if (!Files.exists(sessionDir)) {
                logger.error("Session directory does not exist: {}", sessionDir);
                return false;
            }

            // Find all TTS audio files (speech_*.mp3)
            List<Path> ttsFiles = Files.list(sessionDir)
                .filter(p -> p.getFileName().toString().startsWith("speech_") && p.getFileName().toString().endsWith(".mp3"))
                .sorted()
                .toList();
            if (ttsFiles.isEmpty()) {
                logger.error("No TTS audio files found in session: {}", sessionId);
                return false;
            }

            // Concatenate TTS audio files
            Path ttsConcat = sessionDir.resolve("tts_concat.mp3");
            if (ttsFiles.size() == 1) {
                Files.copy(ttsFiles.get(0), ttsConcat, StandardCopyOption.REPLACE_EXISTING);
            } else {
                // Create file list for ffmpeg
                Path fileList = sessionDir.resolve("tts_files.txt");
                try (BufferedWriter writer = Files.newBufferedWriter(fileList)) {
                    for (Path ttsFile : ttsFiles) {
                        writer.write("file '" + ttsFile.toAbsolutePath() + "'\n");
                    }
                }
                
                // Concatenate TTS files
                ProcessBuilder concatPb = new ProcessBuilder("ffmpeg", "-f", "concat", "-safe", "0", 
                    "-i", fileList.toString(), "-c", "copy", ttsConcat.toString());
                Process concatProcess = concatPb.start();
                int concatExitCode = concatProcess.waitFor();
                if (concatExitCode != 0) {
                    logger.error("Failed to concatenate TTS files, exit code: {}", concatExitCode);
                    return false;
                }
                Files.deleteIfExists(fileList);
            }

            // Find the user's video file (recording.mp4)
            Path userVideo = sessionDir.resolve("recording.mp4");
            if (!Files.exists(userVideo)) {
                logger.error("User video file not found: {}", userVideo);
                return false;
            }

            // Check if user file has video stream
            ProcessBuilder probePb = new ProcessBuilder("ffprobe", "-v", "quiet", "-select_streams", "v", 
                "-show_entries", "stream=codec_type", "-of", "csv=p=0", userVideo.toString());
            Process probeProcess = probePb.start();
            String probeOutput = new String(probeProcess.getInputStream().readAllBytes()).trim();
            boolean hasVideo = !probeOutput.isEmpty();
            logger.info("User file {} has video: {}", userVideo.getFileName(), hasVideo);

            // Mix TTS audio with user video
            Path finalVideo = sessionDir.resolve("final_response.mp4");
            ProcessBuilder mixPb;
            
            if (hasVideo) {
                // User file has video, mix TTS audio with existing video
                mixPb = new ProcessBuilder("ffmpeg", "-i", userVideo.toString(), "-i", ttsConcat.toString(),
                    "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=longest[aout]",
                    "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", finalVideo.toString());
            } else {
                // User file has only audio, create video with black background + mixed audio
                mixPb = new ProcessBuilder("ffmpeg", "-f", "lavfi", "-i", "color=black:size=1280x720:duration=10",
                    "-i", userVideo.toString(), "-i", ttsConcat.toString(),
                    "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=longest[aout]",
                    "-map", "0:v", "-map", "[aout]", "-c:v", "libx264", "-c:a", "aac", "-shortest", finalVideo.toString());
            }

            Process mixProcess = mixPb.start();
            int mixExitCode = mixProcess.waitFor();
            
            // Log the command and result
            String command = String.join(" ", mixPb.command());
            logger.info("ffmpeg mixing for session {} completed with exit code: {}, success: {}", 
                sessionId, mixExitCode, mixExitCode == 0);
            
            if (mixExitCode != 0) {
                String errorOutput = new String(mixProcess.getErrorStream().readAllBytes());
                logger.error("ffmpeg mixing failed: {}", errorOutput);
                return false;
            }

            logger.info("Successfully created mixed video: {}", finalVideo);
            return true;

        } catch (Exception e) {
            logger.error("Error mixing TTS with user video for session {}: {}", sessionId, e.getMessage(), e);
            return false;
        }
    }
} 