package com.interview.grpc;

import com.interview.service.InterviewService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/java")
@CrossOrigin(origins = "*")
public class InterviewRestController {
    
    private static final Logger logger = LoggerFactory.getLogger(InterviewRestController.class);
    
    @Autowired
    private InterviewService interviewService;
    
    @Autowired
    private com.interview.config.InterviewConfig config;
    
    @PostMapping("/start-interview")
    public ResponseEntity<Map<String, Object>> startInterview(@RequestBody Map<String, String> request) {
        try {
            logger.info("Starting interview for client: {}", request.get("client_id"));
            
            // Create gRPC request
            StartInterviewRequest grpcRequest = StartInterviewRequest.newBuilder()
                    .setClientId(request.get("client_id"))
                    .build();
            
            // Call gRPC service
            StartInterviewResponse response = interviewService.startInterview(grpcRequest);
            
            // Convert to HTTP response
            Map<String, Object> httpResponse = new HashMap<>();
            httpResponse.put("success", response.getSuccess());
            httpResponse.put("session_id", response.getSessionId());
            httpResponse.put("greeting_message", response.getGreetingMessage());
            
            logger.info("Interview started successfully with session ID: {}", response.getSessionId());
            return ResponseEntity.ok(httpResponse);
            
        } catch (Exception e) {
            logger.error("Error starting interview", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }
    
    @PostMapping("/generate-question")
    public ResponseEntity<Map<String, Object>> generateQuestion(@RequestBody Map<String, String> request) {
        try {
            logger.info("Generating question for context: {}", request.get("context"));
            
            // Create gRPC request - use context as category
            GetQuestionsRequest grpcRequest = GetQuestionsRequest.newBuilder()
                    .setCategory(request.get("context"))
                    .build();
            
            // Call gRPC service
            GetQuestionsResponse response = interviewService.getInterviewQuestions(grpcRequest);
            
            // Convert to HTTP response
            Map<String, Object> httpResponse = new HashMap<>();
            httpResponse.put("success", true);
            if (response.getQuestionsCount() > 0) {
                httpResponse.put("question", response.getQuestions(0)); // Get first question
            } else {
                httpResponse.put("question", "Tell me about yourself.");
            }
            
            logger.info("Question generated successfully");
            return ResponseEntity.ok(httpResponse);
            
        } catch (Exception e) {
            logger.error("Error generating question", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }
    
    @PostMapping("/generate-followup")
    public ResponseEntity<Map<String, Object>> generateFollowUp(@RequestBody Map<String, String> request) {
        try {
            logger.info("Generating follow-up for context: {}", request.get("context"));
            
            // Create gRPC request - use context as category
            GetQuestionsRequest grpcRequest = GetQuestionsRequest.newBuilder()
                    .setCategory(request.get("context"))
                    .build();
            
            // Call gRPC service
            GetQuestionsResponse response = interviewService.getInterviewQuestions(grpcRequest);
            
            // Convert to HTTP response
            Map<String, Object> httpResponse = new HashMap<>();
            httpResponse.put("success", true);
            if (response.getQuestionsCount() > 0) {
                httpResponse.put("follow_up_question", response.getQuestions(0)); // Get first question
            } else {
                httpResponse.put("follow_up_question", "Can you elaborate on that?");
            }
            
            logger.info("Follow-up question generated successfully");
            return ResponseEntity.ok(httpResponse);
            
        } catch (Exception e) {
            logger.error("Error generating follow-up", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }
    
    @PostMapping(value = "/process-audio", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<Map<String, Object>> processAudio(
            @RequestParam("file") MultipartFile file,
            @RequestParam("session_id") String sessionId,
            @RequestParam("client_id") String clientId) {
        try {
            logger.info("Processing audio for session: {}", sessionId);
            
            // Convert MultipartFile to byte array
            byte[] audioData = file.getBytes();
            
            // Determine audio format from file extension
            String originalFilename = file.getOriginalFilename();
            String audioFormat = "webm"; // default
            if (originalFilename != null) {
                if (originalFilename.toLowerCase().endsWith(".mp4")) {
                    audioFormat = "mp4";
                } else if (originalFilename.toLowerCase().endsWith(".wav")) {
                    audioFormat = "wav";
                } else if (originalFilename.toLowerCase().endsWith(".mp3")) {
                    audioFormat = "mp3";
                } else if (originalFilename.toLowerCase().endsWith(".webm")) {
                    audioFormat = "webm";
                }
            }
            
            logger.info("Detected audio format: {} from filename: {}", audioFormat, originalFilename);
            
            // Create gRPC request
            ProcessAudioRequest grpcRequest = ProcessAudioRequest.newBuilder()
                    .setSessionId(sessionId)
                    .setClientId(clientId)
                    .setAudioData(com.google.protobuf.ByteString.copyFrom(audioData))
                    .setAudioFormat(audioFormat)
                    .build();
            
            // Call gRPC service
            ProcessAudioResponse response = interviewService.processAudio(grpcRequest);
            
            // Convert to HTTP response
            Map<String, Object> httpResponse = new HashMap<>();
            httpResponse.put("success", response.getSuccess());
            httpResponse.put("transcription", response.getTranscription());
            
            logger.info("Audio processed successfully");
            return ResponseEntity.ok(httpResponse);
            
        } catch (Exception e) {
            logger.error("Error processing audio", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }
    
    @PostMapping(value = "/process-video", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<Map<String, Object>> processVideo(
            @RequestParam("file") MultipartFile file,
            @RequestParam("session_id") String sessionId,
            @RequestParam("client_id") String clientId) {
        try {
            logger.info("Processing video for session: {}", sessionId);
            
            // Convert MultipartFile to byte array
            byte[] videoData = file.getBytes();
            
            // Determine video format from file extension
            String originalFilename = file.getOriginalFilename();
            String videoFormat = "webm"; // default
            if (originalFilename != null) {
                if (originalFilename.toLowerCase().endsWith(".mp4")) {
                    videoFormat = "mp4";
                } else if (originalFilename.toLowerCase().endsWith(".webm")) {
                    videoFormat = "webm";
                } else if (originalFilename.toLowerCase().endsWith(".avi")) {
                    videoFormat = "avi";
                } else if (originalFilename.toLowerCase().endsWith(".mov")) {
                    videoFormat = "mov";
                }
            }
            
            logger.info("Detected video format: {} from filename: {}", videoFormat, originalFilename);
            
            // Save video file directly
            String videoFileName = "video_" + System.currentTimeMillis() + "." + videoFormat;
            Path videoPath = config.getRecordingsDir().resolve(sessionId).resolve(videoFileName);
            Files.write(videoPath, videoData);
            
            // Convert to HTTP response
            Map<String, Object> httpResponse = new HashMap<>();
            httpResponse.put("success", true);
            httpResponse.put("video_file_path", videoPath.toString());
            
            logger.info("Video processed successfully, saved to: {}", videoPath);
            return ResponseEntity.ok(httpResponse);
            
        } catch (Exception e) {
            logger.error("Error processing video", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }
    
    @PostMapping("/generate-speech")
    public ResponseEntity<Map<String, Object>> generateSpeech(@RequestBody Map<String, String> request) {
        try {
            logger.info("Generating speech for session: {}", request.get("session_id"));
            
            // Create gRPC request
            GenerateSpeechRequest grpcRequest = GenerateSpeechRequest.newBuilder()
                    .setSessionId(request.get("session_id"))
                    .setText(request.get("text"))
                    .setVoice(request.get("voice"))
                    .build();
            
            // Call gRPC service
            GenerateSpeechResponse response = interviewService.generateSpeech(grpcRequest);
            
            // Convert to HTTP response
            Map<String, Object> httpResponse = new HashMap<>();
            httpResponse.put("success", response.getSuccess());
            
            // Convert byte array to base64 for JSON transmission
            if (response.getSuccess() && response.getAudioData() != null) {
                byte[] audioBytes = response.getAudioData().toByteArray();
                String base64Audio = java.util.Base64.getEncoder().encodeToString(audioBytes);
                httpResponse.put("audio_data", base64Audio);
            }
            
            httpResponse.put("audio_file_path", response.getAudioFilePath());
            
            logger.info("Speech generated successfully");
            return ResponseEntity.ok(httpResponse);
            
        } catch (Exception e) {
            logger.error("Error generating speech", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }
    
    @PostMapping("/finish-interview")
    public ResponseEntity<Map<String, Object>> finishInterview(@RequestBody Map<String, String> request) {
        try {
            logger.info("Finishing interview for session: {}", request.get("session_id"));
            
            // Create gRPC request
            FinishInterviewRequest grpcRequest = FinishInterviewRequest.newBuilder()
                    .setSessionId(request.get("session_id"))
                    .build();
            
            // Call gRPC service
            FinishInterviewResponse response = interviewService.finishInterview(grpcRequest);
            
            // Convert to HTTP response
            Map<String, Object> httpResponse = new HashMap<>();
            httpResponse.put("success", response.getSuccess());
            httpResponse.put("audio_combined", response.getAudioCombined());
            httpResponse.put("video_combined", response.getVideoCombined());
            
            logger.info("Interview finished successfully");
            return ResponseEntity.ok(httpResponse);
            
        } catch (Exception e) {
            logger.error("Error finishing interview", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }
    
    @GetMapping("/list-recordings")
    public ResponseEntity<Map<String, Object>> listRecordings() {
        try {
            logger.info("Listing recordings from directory: {}", config.getRecordingsDir());
            
            Path recordingsDir = config.getRecordingsDir();
            if (!Files.exists(recordingsDir)) {
                logger.info("Recordings directory does not exist, creating it");
                Files.createDirectories(recordingsDir);
            }
            
            List<Map<String, Object>> recordings = new ArrayList<>();
            
            // List all session directories
            List<Path> sessionDirs = Files.list(recordingsDir)
                    .filter(Files::isDirectory)
                    .collect(Collectors.toList());
            
            for (Path sessionDir : sessionDirs) {
                String sessionId = sessionDir.getFileName().toString();
                Map<String, Object> recording = new HashMap<>();
                recording.put("session_id", sessionId);
                
                // Count audio files
                List<Path> audioFiles = Files.list(sessionDir)
                        .filter(path -> {
                            String name = path.getFileName().toString().toLowerCase();
                            return name.endsWith(".mp3") || name.endsWith(".wav") || name.endsWith(".webm");
                        })
                        .collect(Collectors.toList());
                
                // Count video files
                List<Path> videoFiles = Files.list(sessionDir)
                        .filter(path -> {
                            String name = path.getFileName().toString().toLowerCase();
                            return name.endsWith(".mp4") || name.endsWith(".avi") || name.endsWith(".mov");
                        })
                        .collect(Collectors.toList());
                
                recording.put("audio_files", audioFiles.stream()
                        .map(path -> path.getFileName().toString())
                        .collect(Collectors.toList()));
                recording.put("video_files", videoFiles.stream()
                        .map(path -> path.getFileName().toString())
                        .collect(Collectors.toList()));
                
                recordings.add(recording);
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("recordings", recordings);
            
            logger.info("Found {} recording sessions", recordings.size());
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("Error listing recordings", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }
    
    @GetMapping("/session-details")
    public ResponseEntity<Map<String, Object>> getSessionDetails(@RequestParam(value = "session_id", required = true) String sessionId) {
        try {
            logger.info("Getting details for session: {}", sessionId);
            
            Path sessionDir = config.getRecordingsDir().resolve(sessionId);
            if (!Files.exists(sessionDir)) {
                Map<String, Object> errorResponse = new HashMap<>();
                errorResponse.put("success", false);
                errorResponse.put("error", "Session not found");
                return ResponseEntity.notFound().build();
            }
            
            Map<String, Object> session = new HashMap<>();
            session.put("session_id", sessionId);
            
            // Get audio files
            List<Path> audioFiles = Files.list(sessionDir)
                    .filter(path -> {
                        String name = path.getFileName().toString().toLowerCase();
                        return name.endsWith(".mp3") || name.endsWith(".wav") || name.endsWith(".webm");
                    })
                    .collect(Collectors.toList());
            
            // Get video files
            List<Path> videoFiles = Files.list(sessionDir)
                    .filter(path -> {
                        String name = path.getFileName().toString().toLowerCase();
                        return name.endsWith(".mp4") || name.endsWith(".avi") || name.endsWith(".mov");
                    })
                    .collect(Collectors.toList());
            
            session.put("audio_files", audioFiles.stream()
                    .map(path -> path.getFileName().toString())
                    .collect(Collectors.toList()));
            session.put("video_files", videoFiles.stream()
                    .map(path -> path.getFileName().toString())
                    .collect(Collectors.toList()));
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("session", session);
            
            logger.info("Retrieved details for session: {}", sessionId);
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("Error getting session details", e);
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("success", false);
            errorResponse.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(errorResponse);
        }
    }
    
    @GetMapping("/audio/{sessionId}/{filename}")
    public ResponseEntity<byte[]> getAudioFile(@PathVariable String sessionId, @PathVariable String filename) {
        try {
            Path filePath = config.getRecordingsDir().resolve(sessionId).resolve(filename);
            if (!Files.exists(filePath)) {
                return ResponseEntity.notFound().build();
            }
            
            byte[] fileContent = Files.readAllBytes(filePath);
            String contentType = getContentType(filename);
            
            return ResponseEntity.ok()
                    .header("Content-Type", contentType)
                    .header("Content-Disposition", "inline; filename=\"" + filename + "\"")
                    .body(fileContent);
                    
        } catch (Exception e) {
            logger.error("Error serving audio file: {}", e.getMessage());
            return ResponseEntity.internalServerError().build();
        }
    }
    
    @GetMapping("/video/{sessionId}/{filename}")
    public ResponseEntity<byte[]> getVideoFile(@PathVariable String sessionId, @PathVariable String filename) {
        try {
            Path filePath = config.getRecordingsDir().resolve(sessionId).resolve(filename);
            if (!Files.exists(filePath)) {
                return ResponseEntity.notFound().build();
            }
            
            byte[] fileContent = Files.readAllBytes(filePath);
            String contentType = getContentType(filename);
            
            return ResponseEntity.ok()
                    .header("Content-Type", contentType)
                    .header("Content-Disposition", "inline; filename=\"" + filename + "\"")
                    .body(fileContent);
                    
        } catch (Exception e) {
            logger.error("Error serving video file: {}", e.getMessage());
            return ResponseEntity.internalServerError().build();
        }
    }
    
    private String getContentType(String filename) {
        String lowerFilename = filename.toLowerCase();
        if (lowerFilename.endsWith(".mp3")) {
            return "audio/mpeg";
        } else if (lowerFilename.endsWith(".wav")) {
            return "audio/wav";
        } else if (lowerFilename.endsWith(".webm")) {
            return "audio/webm";
        } else if (lowerFilename.endsWith(".mp4")) {
            return "video/mp4";
        } else if (lowerFilename.endsWith(".avi")) {
            return "video/x-msvideo";
        } else if (lowerFilename.endsWith(".mov")) {
            return "video/quicktime";
        } else {
            return "application/octet-stream";
        }
    }
} 