#!/usr/bin/env python3
"""
Service Registry - Central service discovery for A2A research platform.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn


# Pydantic models for API
class ServiceRegistration(BaseModel):
    service_name: str
    host: str
    port: int
    health_endpoint: str = "/health"
    metadata: Dict[str, Any] = {}


class ServiceInfo(BaseModel):
    service_name: str
    host: str
    port: int
    health_endpoint: str
    url: str
    status: str
    registered_at: str
    last_heartbeat: str
    metadata: Dict[str, Any]


class ServiceRegistry:
    """Central service registry for A2A services."""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.services: Dict[str, ServiceInfo] = {}
        self.heartbeat_timeout = 60  # seconds
        
        # Create FastAPI app
        self.app = FastAPI(
            title="A2A Service Registry",
            description="Central service discovery for A2A research platform",
            version="1.0.0"
        )
        
        # Setup routes
        self._setup_routes()
        
        # Note: Health check loop will be started when uvicorn runs the app
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "registry"}
        
        @self.app.post("/register")
        async def register_service(registration: ServiceRegistration):
            """Register a new service."""
            service_url = f"http://{registration.host}:{registration.port}"
            
            service_info = ServiceInfo(
                service_name=registration.service_name,
                host=registration.host,
                port=registration.port,
                health_endpoint=registration.health_endpoint,
                url=service_url,
                status="unknown",
                registered_at=datetime.utcnow().isoformat(),
                last_heartbeat=datetime.utcnow().isoformat(),
                metadata=registration.metadata
            )
            
            self.services[registration.service_name] = service_info
            
            print(f"[registry] Registered service: {registration.service_name} at {service_url}")
            
            return {"status": "registered", "service_name": registration.service_name}
        
        @self.app.post("/heartbeat/{service_name}")
        async def heartbeat(service_name: str):
            """Update service heartbeat."""
            if service_name not in self.services:
                raise HTTPException(status_code=404, detail="Service not found")
            
            self.services[service_name].last_heartbeat = datetime.utcnow().isoformat()
            self.services[service_name].status = "healthy"
            
            return {"status": "heartbeat_received"}
        
        @self.app.get("/services", response_model=List[ServiceInfo])
        async def list_services():
            """List all registered services."""
            return list(self.services.values())
        
        @self.app.get("/services/{service_name}", response_model=ServiceInfo)
        async def get_service(service_name: str):
            """Get information for a specific service."""
            if service_name not in self.services:
                raise HTTPException(status_code=404, detail="Service not found")
            
            return self.services[service_name]
        
        @self.app.delete("/services/{service_name}")
        async def unregister_service(service_name: str):
            """Unregister a service."""
            if service_name not in self.services:
                raise HTTPException(status_code=404, detail="Service not found")
            
            del self.services[service_name]
            print(f"[registry] Unregistered service: {service_name}")
            
            return {"status": "unregistered", "service_name": service_name}
        
        @self.app.get("/discover/{service_name}")
        async def discover_service(service_name: str):
            """Discover a service and return its URL."""
            if service_name not in self.services:
                raise HTTPException(status_code=404, detail="Service not found")
            
            service = self.services[service_name]
            if service.status != "healthy":
                raise HTTPException(status_code=503, detail="Service unhealthy")
            
            return {
                "service_name": service_name,
                "url": service.url,
                "status": service.status
            }
    
    async def _health_check_loop(self):
        """Background task to check service health."""
        import httpx
        
        while True:
            await asyncio.sleep(30)  # Check every 30 seconds
            
            for service_name, service_info in list(self.services.items()):
                try:
                    # Check if last heartbeat is recent
                    last_heartbeat = datetime.fromisoformat(service_info.last_heartbeat)
                    if datetime.utcnow() - last_heartbeat > timedelta(seconds=self.heartbeat_timeout):
                        service_info.status = "unhealthy"
                        print(f"[registry] Service {service_name} marked as unhealthy (no heartbeat)")
                        continue
                    
                    # Perform health check
                    async with httpx.AsyncClient() as client:
                        health_url = f"{service_info.url}{service_info.health_endpoint}"
                        response = await client.get(health_url, timeout=5.0)
                        
                        if response.status_code == 200:
                            service_info.status = "healthy"
                        else:
                            service_info.status = "unhealthy"
                            print(f"[registry] Service {service_name} health check failed: {response.status_code}")
                
                except Exception as e:
                    service_info.status = "unhealthy"
                    print(f"[registry] Service {service_name} health check error: {e}")
    
    def run(self):
        """Run the service registry."""
        print(f"Starting Service Registry on port {self.port}")
        
        # Start health check loop as a startup event
        @self.app.on_event("startup")
        async def startup_event():
            asyncio.create_task(self._health_check_loop())
        
        uvicorn.run(self.app, host="127.0.0.1", port=self.port)


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    registry = ServiceRegistry(port=port)
    registry.run()