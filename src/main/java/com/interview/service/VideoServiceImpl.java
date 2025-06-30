package com.interview.service;

import com.interview.grpc.*;
import org.springframework.stereotype.Service;

@Service
public class VideoServiceImpl implements VideoService {
    @Override
    public AnnotateVideoResponse annotateVideo(AnnotateVideoRequest request) {
        return AnnotateVideoResponse.newBuilder().setSuccess(true).build();
    }
    @Override
    public GenerateSubtitlesResponse generateSubtitles(GenerateSubtitlesRequest request) {
        return GenerateSubtitlesResponse.newBuilder().setSuccess(true).build();
    }
    @Override
    public CreateEnhancedVideoResponse createEnhancedVideo(CreateEnhancedVideoRequest request) {
        return CreateEnhancedVideoResponse.newBuilder().setSuccess(true).build();
    }
} 