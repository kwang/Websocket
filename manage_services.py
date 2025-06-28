#!/usr/bin/env python3
"""
Service management script for AI Interview Agent
"""

import subprocess
import time
import signal
import os
import sys
import requests
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.server_process = None
        self.client_process = None
        self.server_port = 8000
        self.client_port = 8080
        
    def kill_existing_processes(self):
        """Kill any existing processes on the required ports"""
        try:
            # Kill processes on server port
            result = subprocess.run(['lsof', '-ti', str(self.server_port)], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(['kill', '-9', pid])
                        print(f"Killed process {pid} on port {self.server_port}")
            
            # Kill processes on client port
            result = subprocess.run(['lsof', '-ti', str(self.client_port)], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(['kill', '-9', pid])
                        print(f"Killed process {pid} on port {self.client_port}")
                        
        except Exception as e:
            print(f"Warning: Could not kill existing processes: {e}")
    
    def start_server(self):
        """Start the server"""
        try:
            print("🚀 Starting server...")
            self.server_process = subprocess.Popen(
                [sys.executable, 'server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            time.sleep(3)  # Wait for server to start
            
            # Test if server is running
            try:
                response = requests.get(f'http://localhost:{self.server_port}/recordings', timeout=5)
                if response.status_code == 200:
                    print("✅ Server started successfully")
                    return True
                else:
                    print(f"❌ Server failed to start properly (status: {response.status_code})")
                    return False
            except requests.exceptions.RequestException:
                print("❌ Server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def start_client(self):
        """Start the client"""
        try:
            print("🚀 Starting client...")
            self.client_process = subprocess.Popen(
                [sys.executable, 'client.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            time.sleep(2)  # Wait for client to start
            
            # Test if client is running
            try:
                response = requests.get(f'http://localhost:{self.client_port}/', timeout=5)
                if response.status_code == 200 and 'AI Interview Agent' in response.text:
                    print("✅ Client started successfully")
                    return True
                else:
                    print(f"❌ Client failed to start properly (status: {response.status_code})")
                    return False
            except requests.exceptions.RequestException:
                print("❌ Client failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting client: {e}")
            return False
    
    def stop_services(self):
        """Stop all services"""
        print("🛑 Stopping services...")
        
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                print("✅ Server stopped")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("⚠️  Server force killed")
            except Exception as e:
                print(f"⚠️  Error stopping server: {e}")
        
        if self.client_process:
            try:
                self.client_process.terminate()
                self.client_process.wait(timeout=5)
                print("✅ Client stopped")
            except subprocess.TimeoutExpired:
                self.client_process.kill()
                print("⚠️  Client force killed")
            except Exception as e:
                print(f"⚠️  Error stopping client: {e}")
        
        # Kill any remaining processes on the ports
        self.kill_existing_processes()
    
    def check_status(self):
        """Check the status of services"""
        print("🔍 Checking service status...")
        
        # Check server
        try:
            response = requests.get(f'http://localhost:{self.server_port}/recordings', timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server: RUNNING (port {self.server_port})")
                print(f"   📁 Recording sessions: {len(data.get('recordings', []))}")
            else:
                print(f"❌ Server: NOT RESPONDING (port {self.server_port})")
        except requests.exceptions.RequestException:
            print(f"❌ Server: NOT RUNNING (port {self.server_port})")
        
        # Check client
        try:
            response = requests.get(f'http://localhost:{self.client_port}/', timeout=5)
            if response.status_code == 200 and 'AI Interview Agent' in response.text:
                print(f"✅ Client: RUNNING (port {self.client_port})")
            else:
                print(f"❌ Client: NOT RESPONDING (port {self.client_port})")
        except requests.exceptions.RequestException:
            print(f"❌ Client: NOT RUNNING (port {self.client_port})")
    
    def restart_services(self):
        """Restart all services"""
        print("🔄 Restarting services...")
        self.stop_services()
        time.sleep(2)
        self.start_server()
        time.sleep(2)
        self.start_client()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_services()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 manage_services.py [start|stop|restart|status|clean]")
        print("\nCommands:")
        print("  start   - Start server and client")
        print("  stop    - Stop all services")
        print("  restart - Restart all services")
        print("  status  - Check service status")
        print("  clean   - Kill any processes on ports 8000 and 8080")
        return
    
    command = sys.argv[1].lower()
    manager = ServiceManager()
    
    if command == 'start':
        print("🎯 Starting AI Interview Agent Services")
        print("=" * 50)
        manager.kill_existing_processes()
        if manager.start_server():
            if manager.start_client():
                print("\n🎉 All services started successfully!")
                print("🌐 Open http://localhost:8080 in your browser")
                print("\nPress Ctrl+C to stop all services")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Shutting down...")
                    manager.stop_services()
            else:
                manager.stop_services()
        else:
            print("❌ Failed to start services")
    
    elif command == 'stop':
        manager.stop_services()
    
    elif command == 'restart':
        manager.restart_services()
    
    elif command == 'status':
        manager.check_status()
    
    elif command == 'clean':
        print("🧹 Cleaning up processes...")
        manager.kill_existing_processes()
        print("✅ Cleanup completed")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use: start, stop, restart, status, or clean")

if __name__ == "__main__":
    main() 