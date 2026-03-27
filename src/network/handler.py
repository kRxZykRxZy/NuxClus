import os
import platform
import socket
from datetime import datetime
import psutil
import json 
from src.config.setup import config
import subprocess
import uuid
import asyncio

def get_system_info():
    # First cpu_percent call can be 0.0; interval gives real sample.
    cpu = {
        "usage_percent": psutil.cpu_percent(interval=1),
        "per_core_percent": psutil.cpu_percent(interval=1, percpu=True),
        "cores_logical": psutil.cpu_count(logical=True),
        "cores_physical": psutil.cpu_count(logical=False),
        "freq_mhz": (
            psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        ),
    }

    vm = psutil.virtual_memory()
    mem = {
        "total": vm.total,
        "available": vm.available,
        "used": vm.used,
        "percent": vm.percent,
    }

    sm = psutil.swap_memory()
    swap = {
        "total": sm.total,
        "used": sm.used,
        "free": sm.free,
        "percent": sm.percent,
    }

    disks = []
    for p in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(p.mountpoint)
            disks.append({
                "device": p.device,
                "mountpoint": p.mountpoint,
                "fstype": p.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent,
            })
        except PermissionError:
            # Some system partitions may be inaccessible
            continue

    net_io = psutil.net_io_counters()
    net = {
        "bytes_sent": net_io.bytes_sent,
        "bytes_recv": net_io.bytes_recv,
        "packets_sent": net_io.packets_sent,
        "packets_recv": net_io.packets_recv,
    }

    boot = datetime.fromtimestamp(psutil.boot_time()).isoformat()

    return {
        "host": socket.gethostname(),
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "boot_time": boot,
        "cpu": cpu,
        "memory": mem,
        "swap": swap,
        "disks": disks,
        "network": net,
        "process_count": len(psutil.pids()),
        "pid": os.getpid(),
    }

async def run_command(cmd, uid, ws):
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            await ws.send(json.dumps({"type": "command_output", "uid": uid, "line": line.decode().rstrip()}))
        await proc.wait()
        await ws.send(json.dumps({"type": "command_end", "uid": uid, "exit_code": proc.returncode}))
    except Exception as e:
        await ws.send(json.dumps({"type": "command_error", "uid": uid, "error": str(e)}))

async def handle(message, ws):
    if message.get("type") == "stats":
        info = get_system_info()
        await ws.send(json.dumps(info))
    elif message.get("type") == "heartbeat":
        await ws.send(json.dumps({"type": "heartbeat", "timestamp": datetime.now().isoformat()}))
    elif message.get("type") == "command":
        if config.get("enable_command_execution", False):
            cmd_str = message.get("command")
            if cmd_str:
                uid = str(uuid.uuid4())
                await ws.send(json.dumps({"type": "command_start", "uid": uid}))
                await run_command(cmd_str, uid, ws)
            else:
                await ws.send(json.dumps({"type": "error", "message": "No command provided."}))
        else:
            await ws.send(json.dumps({"type": "error", "message": "Command execution is disabled."}))
    elif message.get("type") == "ping":
        await ws.send("pong")
    elif message.get("type") == "config":
        await ws.send(json.dumps({"type": "config", "data": config.data}))

        
