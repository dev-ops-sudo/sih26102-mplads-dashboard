import os

env_path = r'C:\Users\dm790\OneDrive\Desktop\new docker backend\.env'
with open(env_path, 'r') as f:
    lines = f.readlines()

with open(env_path, 'w') as f:
    for line in lines:
        if line.startswith('MPLADS_CORS_ORIGINS'):
            f.write('MPLADS_CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:5174","http://127.0.0.1:5174"]\n')
        else:
            f.write(line)

dc_path = r'C:\Users\dm790\OneDrive\Desktop\new docker backend\docker-compose.yml'
with open(dc_path, 'r') as f:
    lines = f.readlines()

with open(dc_path, 'w') as f:
    for line in lines:
        if 'MPLADS_CORS_ORIGINS:' in line:
            f.write('      MPLADS_CORS_ORIGINS: \\n')
        else:
            f.write(line)
