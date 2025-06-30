package com.interview.examples;

import com.interview.grpc.*;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.stub.StreamObserver;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

public class JavaClientExample {
    
    private final ManagedChannel channel;
    private final InterviewServiceGrpc.InterviewServiceBlockingStub blockingStub;
    private final InterviewServiceGrpc.InterviewServiceStub asyncStub;
    private final InterviewStreamServiceGrpc.InterviewStreamServiceStub streamStub;
    private final FileServiceGrpc.FileServiceStub fileStub;
    
    public JavaClientExample(String host, int port) {
        channel = ManagedChannelBuilder.forAddress(host, port)
                .usePlaintext()
                .maxInboundMessageSize(50 * 1024 * 1024) // 50MB
                .build();
        
        blockingStub = InterviewServiceGrpc.newBlockingStub(channel);
        asyncStub = InterviewServiceGrpc.newStub(channel);
        streamStub = InterviewStreamServiceGrpc.newStub(channel);
        fileStub = FileServiceGrpc.newStub(channel);
    }
    
    public void shutdown() throws InterruptedException {
        channel.shutdown().awaitTermination(5, TimeUnit.SECONDS);
    }
    
    /**
     * Example: Start an interview session
     */
    public void startInterview() {
        System.out.println("=== Starting Interview ===");
        
        StartInterviewRequest request = StartInterviewRequest.newBuilder()
                .setClientId("client_" + System.currentTimeMillis())
                .build();
        
        try {
            StartInterviewResponse response = blockingStub.startInterview(request);
            System.out.println("✅ Interview started successfully!");
            System.out.println("Session ID: " + response.getSessionId());
            System.out.println("Greeting: " + response.getGreetingMessage());
        } catch (Exception e) {
            System.err.println("❌ Failed to start interview: " + e.getMessage());
        }
    }
    
    /**
     * Example: Process audio for transcription
     */
    public void processAudio(String sessionId, String audioFilePath) {
        System.out.println("=== Processing Audio ===");
        
        try {
            byte[] audioData = Files.readAllBytes(Paths.get(audioFilePath));
            
            ProcessAudioRequest request = ProcessAudioRequest.newBuilder()
                    .setAudioData(com.google.protobuf.ByteString.copyFrom(audioData))
                    .setSessionId(sessionId)
                    .setClientId("client123")
                    .setAudioFormat("mp3")
                    .build();
            
            ProcessAudioResponse response = blockingStub.processAudio(request);
            
            if (response.getSuccess()) {
                System.out.println("✅ Audio processed successfully!");
                System.out.println("Transcription: " + response.getTranscription());
                System.out.println("Follow-up: " + response.getFollowUpQuestion());
            } else {
                System.err.println("❌ Audio processing failed: " + response.getErrorMessage());
            }
        } catch (IOException e) {
            System.err.println("❌ Failed to read audio file: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("❌ Failed to process audio: " + e.getMessage());
        }
    }
    
    /**
     * Example: Generate text-to-speech
     */
    public void generateSpeech(String sessionId, String text) {
        System.out.println("=== Generating Speech ===");
        
        GenerateSpeechRequest request = GenerateSpeechRequest.newBuilder()
                .setText(text)
                .setVoice("alloy")
                .setSessionId(sessionId)
                .build();
        
        try {
            GenerateSpeechResponse response = blockingStub.generateSpeech(request);
            
            if (response.getSuccess()) {
                System.out.println("✅ Speech generated successfully!");
                System.out.println("Audio file: " + response.getAudioFilePath());
                System.out.println("Audio size: " + response.getAudioData().size() + " bytes");
                
                // Save the audio to a file
                Files.write(Paths.get("generated_speech.mp3"), response.getAudioData().toByteArray());
                System.out.println("✅ Audio saved to generated_speech.mp3");
            } else {
                System.err.println("❌ Speech generation failed: " + response.getErrorMessage());
            }
        } catch (Exception e) {
            System.err.println("❌ Failed to generate speech: " + e.getMessage());
        }
    }
    
    /**
     * Example: Bidirectional streaming interview
     */
    public void streamingInterview(String sessionId) {
        System.out.println("=== Streaming Interview ===");
        
        CountDownLatch latch = new CountDownLatch(1);
        
        StreamObserver<InterviewMessage> responseObserver = new StreamObserver<InterviewMessage>() {
            @Override
            public void onNext(InterviewMessage message) {
                System.out.println("📨 Received: " + message.getText());
                
                // Send a response back
                InterviewMessage response = InterviewMessage.newBuilder()
                        .setText("Thank you for the question. I'm ready to answer.")
                        .setSessionId(sessionId)
                        .setMessageType(MessageType.ANSWER)
                        .build();
                
                // Note: In a real implementation, you'd need to store the requestObserver
                // and send the response here
            }
            
            @Override
            public void onError(Throwable t) {
                System.err.println("❌ Stream error: " + t.getMessage());
                latch.countDown();
            }
            
            @Override
            public void onCompleted() {
                System.out.println("✅ Stream completed");
                latch.countDown();
            }
        };
        
        StreamObserver<InterviewMessage> requestObserver = streamStub.interviewStream(responseObserver);
        
        try {
            // Send initial greeting
            InterviewMessage greeting = InterviewMessage.newBuilder()
                    .setText("Hello! I'm ready to start the interview.")
                    .setSessionId(sessionId)
                    .setMessageType(MessageType.GREETING)
                    .build();
            
            requestObserver.onNext(greeting);
            
            // Wait for some responses
            Thread.sleep(5000);
            
            // Send another message
            InterviewMessage answer = InterviewMessage.newBuilder()
                    .setText("I have 5 years of experience in software development.")
                    .setSessionId(sessionId)
                    .setMessageType(MessageType.ANSWER)
                    .build();
            
            requestObserver.onNext(answer);
            
            // Wait a bit more
            Thread.sleep(3000);
            
            // Complete the stream
            requestObserver.onCompleted();
            
            // Wait for completion
            latch.await(10, TimeUnit.SECONDS);
            
        } catch (InterruptedException e) {
            System.err.println("❌ Stream interrupted: " + e.getMessage());
        }
    }
    
    /**
     * Example: Upload audio file
     */
    public void uploadAudio(String sessionId, String audioFilePath) {
        System.out.println("=== Uploading Audio ===");
        
        CountDownLatch latch = new CountDownLatch(1);
        
        StreamObserver<UploadResponse> responseObserver = new StreamObserver<UploadResponse>() {
            @Override
            public void onNext(UploadResponse response) {
                if (response.getSuccess()) {
                    System.out.println("✅ Audio uploaded successfully!");
                    System.out.println("Filename: " + response.getFilename());
                    System.out.println("Path: " + response.getFilePath());
                } else {
                    System.err.println("❌ Upload failed: " + response.getErrorMessage());
                }
                latch.countDown();
            }
            
            @Override
            public void onError(Throwable t) {
                System.err.println("❌ Upload error: " + t.getMessage());
                latch.countDown();
            }
            
            @Override
            public void onCompleted() {
                System.out.println("✅ Upload completed");
            }
        };
        
        StreamObserver<AudioChunk> requestObserver = fileStub.uploadAudio(responseObserver);
        
        try {
            byte[] fileData = Files.readAllBytes(Paths.get(audioFilePath));
            String filename = Paths.get(audioFilePath).getFileName().toString();
            
            int chunkSize = 1024 * 1024; // 1MB chunks
            
            for (int i = 0; i < fileData.length; i += chunkSize) {
                int end = Math.min(i + chunkSize, fileData.length);
                byte[] chunk = Arrays.copyOfRange(fileData, i, end);
                
                AudioChunk audioChunk = AudioChunk.newBuilder()
                        .setData(com.google.protobuf.ByteString.copyFrom(chunk))
                        .setSessionId(sessionId)
                        .setFilename(filename)
                        .setIsLastChunk(end == fileData.length)
                        .build();
                
                requestObserver.onNext(audioChunk);
                
                // Small delay to simulate real upload
                Thread.sleep(100);
            }
            
            requestObserver.onCompleted();
            
            // Wait for completion
            latch.await(30, TimeUnit.SECONDS);
            
        } catch (IOException e) {
            System.err.println("❌ Failed to read file: " + e.getMessage());
        } catch (InterruptedException e) {
            System.err.println("❌ Upload interrupted: " + e.getMessage());
        }
    }
    
    /**
     * Example: List recordings
     */
    public void listRecordings() {
        System.out.println("=== Listing Recordings ===");
        
        ListRecordingsRequest request = ListRecordingsRequest.newBuilder()
                .setFilter("") // No filter
                .build();
        
        try {
            ListRecordingsResponse response = blockingStub.listRecordings(request);
            
            System.out.println("📁 Found " + response.getSessionsCount() + " recording sessions:");
            
            for (RecordingSession session : response.getSessionsList()) {
                System.out.println("  Session: " + session.getSessionId());
                System.out.println("    Audio files: " + session.getAudioFilesCount());
                System.out.println("    Video files: " + session.getVideoFilesCount());
                System.out.println("    Start time: " + session.getStartTime());
                System.out.println();
            }
        } catch (Exception e) {
            System.err.println("❌ Failed to list recordings: " + e.getMessage());
        }
    }
    
    /**
     * Example: Finish interview session
     */
    public void finishInterview(String sessionId) {
        System.out.println("=== Finishing Interview ===");
        
        FinishInterviewRequest request = FinishInterviewRequest.newBuilder()
                .setSessionId(sessionId)
                .build();
        
        try {
            FinishInterviewResponse response = blockingStub.finishInterview(request);
            
            if (response.getSuccess()) {
                System.out.println("✅ Interview finished successfully!");
                System.out.println("Audio combined: " + response.getAudioCombined());
                System.out.println("Video combined: " + response.getVideoCombined());
            } else {
                System.err.println("❌ Failed to finish interview: " + response.getErrorMessage());
            }
        } catch (Exception e) {
            System.err.println("❌ Failed to finish interview: " + e.getMessage());
        }
    }
    
    public static void main(String[] args) {
        JavaClientExample client = new JavaClientExample("localhost", 9090);
        
        try {
            // Start an interview
            client.startInterview();
            
            // Simulate a session ID (in real usage, you'd get this from startInterview)
            String sessionId = "interview_20241201_120000_client123";
            
            // Generate some speech
            client.generateSpeech(sessionId, "Hello! Welcome to your interview today.");
            
            // List existing recordings
            client.listRecordings();
            
            // Upload an audio file (if you have one)
            // client.uploadAudio(sessionId, "path/to/audio.mp3");
            
            // Process audio (if you have one)
            // client.processAudio(sessionId, "path/to/audio.mp3");
            
            // Streaming interview
            client.streamingInterview(sessionId);
            
            // Finish the interview
            client.finishInterview(sessionId);
            
        } catch (Exception e) {
            System.err.println("❌ Client error: " + e.getMessage());
            e.printStackTrace();
        } finally {
            try {
                client.shutdown();
            } catch (InterruptedException e) {
                System.err.println("❌ Shutdown error: " + e.getMessage());
            }
        }
    }
} 