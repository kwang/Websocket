#!/usr/bin/env python3
"""
Python gRPC Client for Java Interview Server

This client connects to the Java gRPC server and provides functionality for:
- Interview sessions
- Audio processing and transcription
- Text-to-speech generation
- File uploads and management
- Video processing and annotations
- Streaming interviews
"""

import grpc
import time
import os
import json
from typing import Optional, Dict, Any, Callable

# Import the generated gRPC modules
try:
    import interview_pb2
    import interview_pb2_grpc
    # import file_service_pb2
    # import file_service_pb2_grpc
    # import video_service_pb2
    # import video_service_pb2_grpc
except ImportError:
    print("❌ gRPC modules not found. Please generate them from your .proto files.")
    exit(1)


class JavaInterviewClient:
    """
    Python client for the Java gRPC Interview Server
    """
    def __init__(self, host: str = "localhost", port: int = 9090):
        self.host = host
        self.port = port
        self.channel = None
        self.interview_stub = None
        self.stream_stub = None
        # self.file_stub = None
        # self.video_stub = None
        self.connected = False

    def connect(self) -> bool:
        try:
            self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
            self.interview_stub = interview_pb2_grpc.InterviewServiceStub(self.channel)
            self.stream_stub = interview_pb2_grpc.InterviewStreamServiceStub(self.channel)
            # self.file_stub = file_service_pb2_grpc.FileServiceStub(self.channel)
            # self.video_stub = video_service_pb2_grpc.VideoServiceStub(self.channel)
            # Test connection
            self._test_connection()
            self.connected = True
            print(f"✅ Connected to Java gRPC server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            self.connected = False
            return False

    def disconnect(self):
        if self.channel:
            self.channel.close()
        self.connected = False
        print("🔌 Disconnected from server")

    def _test_connection(self):
        try:
            request = interview_pb2.GetQuestionsRequest()
            self.interview_stub.GetInterviewQuestions(request, timeout=5)
        except Exception as e:
            raise Exception(f"Connection test failed: {e}")

    def start_interview(self, client_id: str = None) -> Dict[str, Any]:
        if not self.connected:
            raise Exception("Not connected to server")
        try:
            if not client_id:
                client_id = f"client_{int(time.time())}"
            request = interview_pb2.StartInterviewRequest(client_id=client_id)
            response = self.interview_stub.StartInterview(request)
            return {
                "success": True,
                "session_id": response.session_id,
                "greeting_message": response.greeting_message,
                "client_id": client_id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def process_audio(self, session_id: str, audio_data: bytes, audio_format: str = "mp3", client_id: str = None) -> Dict[str, Any]:
        if not self.connected:
            raise Exception("Not connected to server")
        try:
            request = interview_pb2.ProcessAudioRequest(
                audio_data=audio_data,
                session_id=session_id,
                client_id=client_id or "unknown",
                audio_format=audio_format
            )
            response = self.interview_stub.ProcessAudio(request)
            return {
                "success": response.success,
                "transcription": response.transcription,
                "follow_up_question": response.follow_up_question,
                "error_message": response.error_message if not response.success else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_speech(self, text: str, session_id: str = None, voice: str = "alloy") -> Dict[str, Any]:
        if not self.connected:
            raise Exception("Not connected to server")
        try:
            request = interview_pb2.GenerateSpeechRequest(
                text=text,
                voice=voice,
                session_id=session_id or ""
            )
            response = self.interview_stub.GenerateSpeech(request)
            return {
                "success": response.success,
                "audio_data": response.audio_data,
                "audio_file_path": response.audio_file_path,
                "error_message": response.error_message if not response.success else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_questions(self) -> Dict[str, Any]:
        if not self.connected:
            raise Exception("Not connected to server")
        try:
            request = interview_pb2.GetQuestionsRequest()
            response = self.interview_stub.GetInterviewQuestions(request)
            return {"success": True, "questions": list(response.questions)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def finish_interview(self, session_id: str) -> Dict[str, Any]:
        if not self.connected:
            raise Exception("Not connected to server")
        try:
            request = interview_pb2.FinishInterviewRequest(session_id=session_id)
            response = self.interview_stub.FinishInterview(request)
            return {
                "success": response.success,
                "audio_combined": response.audio_combined,
                "video_combined": response.video_combined,
                "error_message": response.error_message if not response.success else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def streaming_interview(self, session_id: str, message_handler: Callable[[str], str] = None):
        if not self.connected:
            raise Exception("Not connected to server")
        def message_stream():
            try:
                def request_iter():
                    # Initial greeting
                    yield interview_pb2.InterviewMessage(
                        text="Hello! I'm ready to start the interview.",
                        session_id=session_id,
                        message_type=interview_pb2.GREETING
                    )
                    while True:
                        if message_handler:
                            reply = message_handler(input("Server: "))
                            if reply:
                                yield interview_pb2.InterviewMessage(
                                    text=reply,
                                    session_id=session_id,
                                    message_type=interview_pb2.ANSWER
                                )
                        time.sleep(1)
                responses = self.stream_stub.InterviewStream(request_iter())
                for response in responses:
                    print(f"📨 Server: {getattr(response, 'text', '')}")
            except Exception as e:
                print(f"❌ Stream error: {e}")
        import threading
        stream_thread = threading.Thread(target=message_stream)
        stream_thread.daemon = True
        stream_thread.start()
        return stream_thread


class JavaInterviewClientCLI:
    def __init__(self, host: str = "localhost", port: int = 9090):
        self.client = JavaInterviewClient(host, port)
        self.current_session = None

    def run(self):
        print("🎤 Java Interview Client CLI")
        print("=" * 40)
        if not self.client.connect():
            print("❌ Failed to connect to server. Exiting.")
            return
        try:
            while True:
                self._show_menu()
                choice = input("\nEnter your choice: ").strip()
                if choice == "1":
                    self._start_interview()
                elif choice == "2":
                    self._process_audio()
                elif choice == "3":
                    self._generate_speech()
                elif choice == "4":
                    self._finish_interview()
                elif choice == "5":
                    self._get_questions()
                elif choice == "6":
                    self._streaming_interview()
                elif choice == "0":
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
                input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        finally:
            self.client.disconnect()

    def _show_menu(self):
        print("\n📋 Main Menu:")
        print("1. Start Interview")
        print("2. Process Audio (from file)")
        print("3. Generate Speech")
        print("4. Finish Interview")
        print("5. Get Questions")
        print("6. Streaming Interview")
        print("0. Exit")

    def _start_interview(self):
        print("\n🎤 Starting Interview...")
        client_id = input("Enter client ID (or press Enter for auto): ").strip() or None
        result = self.client.start_interview(client_id)
        if result["success"]:
            self.current_session = result["session_id"]
            print(f"✅ Interview started! Session ID: {result['session_id']}")
            print(f"Greeting: {result['greeting_message']}")
        else:
            print(f"❌ Failed to start interview: {result['error']}")

    def _process_audio(self):
        if not self.current_session:
            print("❌ No active session. Please start an interview first.")
            return
        print("\n🎵 Process Audio...")
        file_path = input("Enter audio file path: ").strip()
        if not os.path.exists(file_path):
            print("❌ File not found.")
            return
        with open(file_path, 'rb') as f:
            audio_data = f.read()
        result = self.client.process_audio(self.current_session, audio_data)
        if result["success"]:
            print(f"✅ Audio processed! Transcription: {result['transcription']}")
            print(f"Follow-up: {result['follow_up_question']}")
        else:
            print(f"❌ Failed to process audio: {result['error']}")

    def _generate_speech(self):
        print("\n🔊 Generate Speech...")
        text = input("Enter text to convert: ").strip()
        if not text:
            print("❌ No text provided.")
            return
        voice = input("Enter voice (alloy/echo/fable/onyx/nova/shimmer) [alloy]: ").strip() or "alloy"
        result = self.client.generate_speech(text, self.current_session, voice)
        if result["success"]:
            print(f"✅ Speech generated! Audio size: {len(result['audio_data'])} bytes")
            output_path = f"generated_speech_{int(time.time())}.mp3"
            with open(output_path, 'wb') as f:
                f.write(result['audio_data'])
            print(f"✅ Saved to: {output_path}")
        else:
            print(f"❌ Failed to generate speech: {result['error']}")

    def _finish_interview(self):
        if not self.current_session:
            print("❌ No active session.")
            return
        print(f"\n🏁 Finishing Interview: {self.current_session}")
        result = self.client.finish_interview(self.current_session)
        if result["success"]:
            print(f"✅ Interview finished! Audio combined: {result['audio_combined']}, Video combined: {result['video_combined']}")
            self.current_session = None
        else:
            print(f"❌ Failed to finish interview: {result['error']}")

    def _get_questions(self):
        print("\n❓ Getting Questions...")
        result = self.client.get_questions()
        if result["success"]:
            print(f"✅ Found {len(result['questions'])} question(s):")
            for i, question in enumerate(result['questions'], 1):
                print(f"  {i}. {question}")
        else:
            print(f"❌ Failed to get questions: {result['error']}")

    def _streaming_interview(self):
        if not self.current_session:
            print("❌ No active session. Please start an interview first.")
            return
        print("\n🔄 Starting Streaming Interview... Press Ctrl+C to stop.")
        def message_handler(message):
            print(f"💬 Received: {message}")
            reply = input("Your response (or press Enter to skip): ").strip()
            return reply if reply else None
        try:
            self.client.streaming_interview(self.current_session, message_handler)
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Streaming stopped")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Java Interview Client")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=9090, help="Server port")
    parser.add_argument("--cli", action="store_true", help="Run CLI interface")
    args = parser.parse_args()
    if args.cli:
        cli = JavaInterviewClientCLI(args.host, args.port)
        cli.run()
    else:
        client = JavaInterviewClient(args.host, args.port)
        if client.connect():
            print("✅ Connected to server!")
            result = client.start_interview()
            if result["success"]:
                print(f"✅ Interview started: {result['session_id']}")
                questions = client.get_questions()
                if questions["success"]:
                    print(f"✅ Found {len(questions['questions'])} questions")
                speech = client.generate_speech("Hello, welcome to the interview!")
                if speech["success"]:
                    print(f"✅ Speech generated: {len(speech['audio_data'])} bytes")
            client.disconnect()
        else:
            print("❌ Failed to connect to server")

if __name__ == "__main__":
    main() 