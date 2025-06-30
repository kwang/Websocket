package com.interview.service;

import com.interview.grpc.*;

public interface InterviewService {
    
    /**
     * Start a new interview session
     */
    StartInterviewResponse startInterview(StartInterviewRequest request);
    
    /**
     * Process audio for transcription and generate follow-up question
     */
    ProcessAudioResponse processAudio(ProcessAudioRequest request);
    
    /**
     * Generate text-to-speech for interviewer questions
     */
    GenerateSpeechResponse generateSpeech(GenerateSpeechRequest request);
    
    /**
     * Finish interview session and combine recordings
     */
    FinishInterviewResponse finishInterview(FinishInterviewRequest request);
    
    /**
     * Get interview questions by category
     */
    GetQuestionsResponse getInterviewQuestions(GetQuestionsRequest request);
    
    /**
     * Process streaming messages for real-time interview
     */
    InterviewMessage processStreamMessage(InterviewMessage message);
} 