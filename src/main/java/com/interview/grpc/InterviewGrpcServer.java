package com.interview.grpc;

import com.interview.config.InterviewConfig;
import com.interview.service.*;
import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.stub.StreamObserver;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

@Component
public class InterviewGrpcServer {
    
    private static final Logger logger = LoggerFactory.getLogger(InterviewGrpcServer.class);
    
    @Autowired
    private InterviewConfig config;
    
    @Autowired
    private InterviewService interviewService;
    
    @Autowired
    private FileService fileService;
    
    @Autowired
    private VideoService videoService;
    
    private Server server;
    
    @PostConstruct
    public void start() throws IOException {
        int port = config.getGrpcPort();
        
        server = ServerBuilder.forPort(port)
                .addService(new InterviewServiceImpl(interviewService))
                .addService(new InterviewStreamServiceImpl(interviewService))
                .addService(new FileServiceImpl(fileService))
                .addService(new VideoServiceImpl(videoService))
                .maxInboundMessageSize(config.getMaxMessageSize())
                .build()
                .start();
        
        logger.info("✅ gRPC Server started on port {}", port);
        
        // Add shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            logger.info("Shutting down gRPC server...");
            try {
                InterviewGrpcServer.this.stop();
            } catch (InterruptedException e) {
                logger.error("Error during server shutdown", e);
            }
        }));
    }
    
    @PreDestroy
    public void stop() throws InterruptedException {
        if (server != null) {
            server.shutdown().awaitTermination(30, TimeUnit.SECONDS);
        }
    }
    
    public void blockUntilShutdown() throws InterruptedException {
        if (server != null) {
            server.awaitTermination();
        }
    }
    
    // Interview Service Implementation
    private static class InterviewServiceImpl extends InterviewServiceGrpc.InterviewServiceImplBase {
        
        private final InterviewService interviewService;
        
        public InterviewServiceImpl(InterviewService interviewService) {
            this.interviewService = interviewService;
        }
        
        @Override
        public void startInterview(StartInterviewRequest request, 
                                 StreamObserver<StartInterviewResponse> responseObserver) {
            try {
                StartInterviewResponse response = interviewService.startInterview(request);
                responseObserver.onNext(response);
                responseObserver.onCompleted();
            } catch (Exception e) {
                logger.error("Error starting interview", e);
                responseObserver.onError(e);
            }
        }
        
        @Override
        public void processAudio(ProcessAudioRequest request, 
                               StreamObserver<ProcessAudioResponse> responseObserver) {
            try {
                ProcessAudioResponse response = interviewService.processAudio(request);
                responseObserver.onNext(response);
                responseObserver.onCompleted();
            } catch (Exception e) {
                logger.error("Error processing audio", e);
                responseObserver.onError(e);
            }
        }
        
        @Override
        public void generateSpeech(GenerateSpeechRequest request, 
                                 StreamObserver<GenerateSpeechResponse> responseObserver) {
            try {
                GenerateSpeechResponse response = interviewService.generateSpeech(request);
                responseObserver.onNext(response);
                responseObserver.onCompleted();
            } catch (Exception e) {
                logger.error("Error generating speech", e);
                responseObserver.onError(e);
            }
        }
        
        @Override
        public void finishInterview(FinishInterviewRequest request, 
                                  StreamObserver<FinishInterviewResponse> responseObserver) {
            try {
                FinishInterviewResponse response = interviewService.finishInterview(request);
                responseObserver.onNext(response);
                responseObserver.onCompleted();
            } catch (Exception e) {
                logger.error("Error finishing interview", e);
                responseObserver.onError(e);
            }
        }
        
        @Override
        public void getInterviewQuestions(GetQuestionsRequest request, 
                                        StreamObserver<GetQuestionsResponse> responseObserver) {
            try {
                GetQuestionsResponse response = interviewService.getInterviewQuestions(request);
                responseObserver.onNext(response);
                responseObserver.onCompleted();
            } catch (Exception e) {
                logger.error("Error getting interview questions", e);
                responseObserver.onError(e);
            }
        }
    }
    
    // Interview Stream Service Implementation
    private static class InterviewStreamServiceImpl extends InterviewStreamServiceGrpc.InterviewStreamServiceImplBase {
        
        private final InterviewService interviewService;
        
        public InterviewStreamServiceImpl(InterviewService interviewService) {
            this.interviewService = interviewService;
        }
        
        @Override
        public StreamObserver<InterviewMessage> interviewStream(StreamObserver<InterviewMessage> responseObserver) {
            return new StreamObserver<InterviewMessage>() {
                @Override
                public void onNext(InterviewMessage message) {
                    try {
                        InterviewMessage response = interviewService.processStreamMessage(message);
                        responseObserver.onNext(response);
                    } catch (Exception e) {
                        logger.error("Error processing stream message", e);
                        InterviewMessage errorMessage = InterviewMessage.newBuilder()
                                .setEvent(InterviewEvent.newBuilder()
                                        .setEventType(EventType.ERROR)
                                        .setMessage("Error processing message: " + e.getMessage())
                                        .build())
                                .setMessageType(MessageType.EVENT)
                                .build();
                        responseObserver.onNext(errorMessage);
                    }
                }
                
                @Override
                public void onError(Throwable t) {
                    logger.error("Stream error", t);
                    responseObserver.onError(t);
                }
                
                @Override
                public void onCompleted() {
                    logger.info("Stream completed");
                    responseObserver.onCompleted();
                }
            };
        }
    }
    
    // File Service Implementation
    private static class FileServiceImpl extends FileServiceGrpc.FileServiceImplBase {
        
        private final FileService fileService;
        
        public FileServiceImpl(FileService fileService) {
            this.fileService = fileService;
        }
        
        @Override
        public StreamObserver<AudioChunk> uploadAudio(StreamObserver<UploadResponse> responseObserver) {
            return new StreamObserver<AudioChunk>() {
                private final StringBuilder sessionId = new StringBuilder();
                private final StringBuilder filename = new StringBuilder();
                private final java.io.ByteArrayOutputStream audioData = new java.io.ByteArrayOutputStream();
                
                @Override
                public void onNext(AudioChunk chunk) {
                    try {
                        if (sessionId.length() == 0) {
                            sessionId.append(chunk.getSessionId());
                        }
                        if (filename.length() == 0) {
                            filename.append(chunk.getFilename());
                        }
                        chunk.getData().writeTo(audioData);
                        
                        if (chunk.getIsLastChunk()) {
                            UploadResponse response = fileService.uploadAudio(
                                    sessionId.toString(),
                                    filename.toString(),
                                    audioData.toByteArray()
                            );
                            responseObserver.onNext(response);
                            responseObserver.onCompleted();
                        }
                    } catch (Exception e) {
                        logger.error("Error uploading audio", e);
                        responseObserver.onError(e);
                    }
                }
                
                @Override
                public void onError(Throwable t) {
                    logger.error("Audio upload stream error", t);
                    responseObserver.onError(t);
                }
                
                @Override
                public void onCompleted() {
                    // Handled in onNext when isLastChunk is true
                }
            };
        }
        
        @Override
        public StreamObserver<VideoChunk> uploadVideo(StreamObserver<UploadResponse> responseObserver) {
            return new StreamObserver<VideoChunk>() {
                private final StringBuilder sessionId = new StringBuilder();
                private final StringBuilder filename = new StringBuilder();
                private final java.io.ByteArrayOutputStream videoData = new java.io.ByteArrayOutputStream();
                
                @Override
                public void onNext(VideoChunk chunk) {
                    try {
                        if (sessionId.length() == 0) {
                            sessionId.append(chunk.getSessionId());
                        }
                        if (filename.length() == 0) {
                            filename.append(chunk.getFilename());
                        }
                        chunk.getData().writeTo(videoData);
                        
                        if (chunk.getIsLastChunk()) {
                            UploadResponse response = fileService.uploadVideo(
                                    sessionId.toString(),
                                    filename.toString(),
                                    videoData.toByteArray()
                            );
                            responseObserver.onNext(response);
                            responseObserver.onCompleted();
                        }
                    } catch (Exception e) {
                        logger.error("Error uploading video", e);
                        responseObserver.onError(e);
                    }
                }
                
                @Override
                public void onError(Throwable t) {
                    logger.error("Video upload stream error", t);
                    responseObserver.onError(t);
                }
                
                @Override
                public void onCompleted() {
                    // Handled in onNext when isLastChunk is true
                }
            };
        }
        
        @Override
        public void downloadFile(DownloadRequest request, StreamObserver<FileChunk> responseObserver) {
            try {
                fileService.downloadFile(request.getSessionId(), request.getFilename(), responseObserver);
            } catch (Exception e) {
                logger.error("Error downloading file", e);
                responseObserver.onError(e);
            }
        }
        
        @Override
        public void listRecordings(ListRecordingsRequest request, 
                                 StreamObserver<ListRecordingsResponse> responseObserver) {
            try {
                ListRecordingsResponse response = fileService.listRecordings(request.getFilter());
                responseObserver.onNext(response);
                responseObserver.onCompleted();
            } catch (Exception e) {
                logger.error("Error listing recordings", e);
                responseObserver.onError(e);
            }
        }
        
        @Override
        public void getSessionRecordings(GetSessionRequest request, 
                                       StreamObserver<GetSessionResponse> responseObserver) {
            try {
                GetSessionResponse response = fileService.getSessionRecordings(request.getSessionId());
                responseObserver.onNext(response);
                responseObserver.onCompleted();
            } catch (Exception e) {
                logger.error("Error getting session recordings", e);
                responseObserver.onError(e);
            }
        }
    }
    
    // Video Service Implementation
    private static class VideoServiceImpl extends VideoServiceGrpc.VideoServiceImplBase {
        
        private final VideoService videoService;
        
        public VideoServiceImpl(VideoService videoService) {
            this.videoService = videoService;
        }
        
        @Override
        public void annotateVideo(AnnotateVideoRequest request, 
                                StreamObserver<AnnotateVideoResponse> responseObserver) {
            try {
                AnnotateVideoResponse response = videoService.annotateVideo(request);
                responseObserver.onNext(response);
                responseObserver.onCompleted();
            } catch (Exception e) {
                logger.error("Error annotating video", e);
                responseObserver.onError(e);
            }
        }
        
        @Override
        public void generateSubtitles(GenerateSubtitlesRequest request, 
                                    StreamObserver<GenerateSubtitlesResponse> responseObserver) {
            try {
                GenerateSubtitlesResponse response = videoService.generateSubtitles(request);
                responseObserver.onNext(response);
                responseObserver.onCompleted();
            } catch (Exception e) {
                logger.error("Error generating subtitles", e);
                responseObserver.onError(e);
            }
        }
        
        @Override
        public void createEnhancedVideo(CreateEnhancedVideoRequest request, 
                                      StreamObserver<CreateEnhancedVideoResponse> responseObserver) {
            try {
                CreateEnhancedVideoResponse response = videoService.createEnhancedVideo(request);
                responseObserver.onNext(response);
                responseObserver.onCompleted();
            } catch (Exception e) {
                logger.error("Error creating enhanced video", e);
                responseObserver.onError(e);
            }
        }
    }
} 