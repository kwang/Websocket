package com.interview.service;

import com.interview.grpc.*;

public interface VideoService {
    
    /**
     * Annotate video with overlays
     */
    AnnotateVideoResponse annotateVideo(AnnotateVideoRequest request);
    
    /**
     * Generate subtitles for video
     */
    GenerateSubtitlesResponse generateSubtitles(GenerateSubtitlesRequest request);
    
    /**
     * Create enhanced video with multiple features
     */
    CreateEnhancedVideoResponse createEnhancedVideo(CreateEnhancedVideoRequest request);
} 