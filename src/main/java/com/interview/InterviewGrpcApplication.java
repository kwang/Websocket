package com.interview;

import com.interview.grpc.InterviewGrpcServer;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.ConfigurableApplicationContext;

@SpringBootApplication
@EnableConfigurationProperties
public class InterviewGrpcApplication {
    
    public static void main(String[] args) {
        ConfigurableApplicationContext context = SpringApplication.run(InterviewGrpcApplication.class, args);
        
        // Get the gRPC server bean and block until shutdown
        InterviewGrpcServer grpcServer = context.getBean(InterviewGrpcServer.class);
        
        try {
            grpcServer.blockUntilShutdown();
        } catch (InterruptedException e) {
            System.err.println("Server interrupted: " + e.getMessage());
        }
    }
} 