dc_path = r'C:\Users\dm790\OneDrive\Desktop\new docker backend\docker-compose.yml'
with open(dc_path, 'r') as f:
    lines = f.readlines()

with open(dc_path, 'w') as f:
    for line in lines:
        if 'MPLADS_CORS_ORIGINS:' in line:
            f.write("      MPLADS_CORS_ORIGINS: ''\n")
        else:
            f.write(line)
