#!/usr/bin/env python3
#test script for multiple Celery submissions

import requests
import json
import time

def submit_request(prompt, fps=24):
    
    try:
        payload = {"prompt": prompt, "fps": fps}
        
        response = requests.post(
            "http://localhost:8000/api/v1/generate",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"'{prompt}' -> {data['job_id']}")
            
            return data['job_id']
        
        else:
            print(f"Failed: {response.status_code}")
            return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

#test prompts
prompts = [
    "A Buddist monk meditating in a temple",
    "A jet fighter flying over the ocean",
]

print(f"Submitting {len(prompts)} generation requests")

job_ids = []

for i, prompt in enumerate(prompts, 1):
    
    print(f"{i}/5: ", end="")
    
    job_id = submit_request(prompt)
    job_ids.append(job_id)
    
    time.sleep(0.5)  

print(f"\nSubmitted {len([jid for jid in job_ids if jid])} requests successfully")

print("Check job status with:")

for job_id in job_ids:
    if job_id:
        print(f"   curl http://localhost:8000/api/v1/job/{job_id}")
