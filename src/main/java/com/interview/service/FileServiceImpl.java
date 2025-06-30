package com.interview.service;

import com.interview.grpc.*;
import io.grpc.stub.StreamObserver;
import org.springframework.stereotype.Service;

@Service
public class FileServiceImpl implements FileService {
    @Override
    public UploadResponse uploadAudio(String sessionId, String filename, byte[] audioData) {
        return UploadResponse.newBuilder().setSuccess(true).setFilename(filename).build();
    }
    @Override
    public UploadResponse uploadVideo(String sessionId, String filename, byte[] videoData) {
        return UploadResponse.newBuilder().setSuccess(true).setFilename(filename).build();
    }
    @Override
    public void downloadFile(String sessionId, String filename, StreamObserver<FileChunk> responseObserver) {
        responseObserver.onCompleted();
    }
    @Override
    public ListRecordingsResponse listRecordings(String filter) {
        return ListRecordingsResponse.newBuilder().build();
    }
    @Override
    public GetSessionResponse getSessionRecordings(String sessionId) {
        return GetSessionResponse.newBuilder().setSuccess(true).build();
    }
} 