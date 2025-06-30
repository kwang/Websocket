package com.interview.service;

import com.interview.grpc.*;
import io.grpc.stub.StreamObserver;

public interface FileService {
    
    /**
     * Upload audio file
     */
    UploadResponse uploadAudio(String sessionId, String filename, byte[] audioData);
    
    /**
     * Upload video file
     */
    UploadResponse uploadVideo(String sessionId, String filename, byte[] videoData);
    
    /**
     * Download file as stream
     */
    void downloadFile(String sessionId, String filename, StreamObserver<FileChunk> responseObserver);
    
    /**
     * List all recordings
     */
    ListRecordingsResponse listRecordings(String filter);
    
    /**
     * Get recordings for a specific session
     */
    GetSessionResponse getSessionRecordings(String sessionId);
} 