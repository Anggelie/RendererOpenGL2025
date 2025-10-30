fragment_shader = """
#version 330 core

in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;

out vec4 outColor;

uniform sampler2D uTexture0;
uniform bool      uHasTexture;
uniform vec3      uLightPos;
uniform vec3      uViewPos;
uniform vec3      uColor;

void main() {
    vec3 N = normalize(fin.normal);
    vec3 L = normalize(uLightPos - fin.worldPos);
    vec3 V = normalize(uViewPos - fin.worldPos);
    
    vec3 base = uHasTexture ? texture(uTexture0, fin.uv).rgb : uColor;
    
    vec3 ambient = 0.2 * base;
    float NdotL = max(dot(N, L), 0.0);
    vec3 diffuse = NdotL * base;
    
    vec3 H = normalize(L + V);
    float spec = pow(max(dot(N, H), 0.0), 64.0);
    vec3 specular = 0.5 * spec * vec3(1.0);
    
    vec3 color = ambient + diffuse + specular;
    outColor = vec4(color, 1.0);
}
"""

toon_shader = """
#version 330 core

in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;

out vec4 outColor;

uniform sampler2D uTexture0;
uniform bool      uHasTexture;
uniform vec3      uLightPos;
uniform vec3      uViewPos;
uniform vec3      uColor;

void main() {
    vec3 N = normalize(fin.normal);
    vec3 L = normalize(uLightPos - fin.worldPos);
    vec3 V = normalize(uViewPos - fin.worldPos);
    
    float NdotL = max(dot(N, L), 0.0);
    float NdotV = max(dot(N, V), 0.0);
    
    float levels = 4.0;
    float toon = floor(NdotL * levels) / levels;
    
    vec3 base = uHasTexture ? texture(uTexture0, fin.uv).rgb : uColor;
    float outline = NdotV > 0.3 ? 1.0 : 0.0;
    
    vec3 color = (0.15 + toon * 0.85) * base * outline;
    outColor = vec4(color, 1.0);
}
"""

rainbow_shader = """
#version 330 core

in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;

out vec4 outColor;

uniform vec3  uLightPos;
uniform float uTime;

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    vec3 N = normalize(fin.normal);
    vec3 L = normalize(uLightPos - fin.worldPos);
    float NdotL = max(dot(N, L), 0.0);
    
    float hue = fract(fin.worldPos.y * 0.5 + fin.worldPos.x * 0.3 + uTime * 0.1);
    vec3 rainbow = hsv2rgb(vec3(hue, 0.8, 1.0));
    
    vec3 color = rainbow * (0.3 + 0.7 * NdotL);
    outColor = vec4(color, 1.0);
}
"""

holographic_shader = """
#version 330 core

in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;

out vec4 outColor;

uniform vec3  uViewPos;
uniform float uTime;

void main() {
    vec3 N = normalize(fin.normal);
    vec3 V = normalize(uViewPos - fin.worldPos);
    
    float fresnel = pow(1.0 - max(dot(N, V), 0.0), 3.0);
    float stripes = sin(fin.worldPos.y * 20.0 + uTime * 3.0) * 0.5 + 0.5;
    
    vec3 color1 = vec3(0.0, 1.0, 1.0);
    vec3 color2 = vec3(1.0, 0.0, 1.0);
    vec3 color3 = vec3(1.0, 1.0, 0.0);
    
    vec3 finalColor = mix(color1, color2, stripes);
    finalColor = mix(finalColor, color3, fresnel);
    
    outColor = vec4(finalColor * (0.5 + 0.5 * fresnel), 0.8 + 0.2 * fresnel);
}
"""

glitch_shader = """
#version 330 core

in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;

out vec4 outColor;

uniform sampler2D uTexture0;
uniform bool      uHasTexture;
uniform vec3      uColor;
uniform float     uTime;

float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
}

void main() {
    vec2 uv = fin.uv;
    
    float glitchStrength = step(0.98, random(vec2(uTime * 0.5)));
    float offset = (random(vec2(uTime, uv.y)) - 0.5) * 0.1 * glitchStrength;
    uv.x += offset;
    
    vec3 base = uHasTexture ? texture(uTexture0, uv).rgb : uColor;
    
    float r = uHasTexture ? texture(uTexture0, uv + vec2(0.01, 0.0) * glitchStrength).r : base.r;
    float g = uHasTexture ? texture(uTexture0, uv).g : base.g;
    float b = uHasTexture ? texture(uTexture0, uv - vec2(0.01, 0.0) * glitchStrength).b : base.b;
    
    vec3 color = vec3(r, g, b);
    float scanline = sin(uv.y * 800.0 + uTime * 10.0) * 0.05 + 0.95;
    color *= scanline;
    
    outColor = vec4(color, 1.0);
}
"""

xray_shader = """
#version 330 core

in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;

out vec4 outColor;

uniform vec3 uViewPos;

void main() {
    vec3 N = normalize(fin.normal);
    vec3 V = normalize(uViewPos - fin.worldPos);
    
    float fresnel = 1.0 - max(dot(N, V), 0.0);
    fresnel = pow(fresnel, 2.0);
    
    vec3 xrayColor = vec3(0.0, 0.5, 1.0);
    vec3 color = xrayColor * fresnel * 2.0;
    
    outColor = vec4(color, fresnel);
}
"""

fire_shader = """
#version 330 core

in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;

out vec4 outColor;

uniform vec3  uLightPos;
uniform float uTime;

void main() {
    vec3 N = normalize(fin.normal);
    vec3 L = normalize(uLightPos - fin.worldPos);
    float NdotL = max(dot(N, L), 0.0);
    
    float noise = fract(sin(dot(fin.worldPos.xy + uTime, vec2(12.9898, 78.233))) * 43758.5453);
    float fire = pow(noise * NdotL, 0.5);
    
    vec3 color = vec3(0.0);
    if (fire < 0.3) {
        color = mix(vec3(0.2, 0.0, 0.0), vec3(1.0, 0.0, 0.0), fire / 0.3);
    } else if (fire < 0.6) {
        color = mix(vec3(1.0, 0.0, 0.0), vec3(1.0, 0.5, 0.0), (fire - 0.3) / 0.3);
    } else if (fire < 0.9) {
        color = mix(vec3(1.0, 0.5, 0.0), vec3(1.0, 1.0, 0.0), (fire - 0.6) / 0.3);
    } else {
        color = mix(vec3(1.0, 1.0, 0.0), vec3(1.0, 1.0, 1.0), (fire - 0.9) / 0.1);
    }
    
    outColor = vec4(color, 1.0);
}
"""

wireframe_shader = """
#version 330 core

in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;

out vec4 outColor;

uniform sampler2D uTexture0;
uniform bool      uHasTexture;
uniform vec3      uColor;
uniform vec3      uLightPos;

void main() {
    vec3 N = normalize(fin.normal);
    vec3 L = normalize(uLightPos - fin.worldPos);
    float NdotL = max(dot(N, L), 0.0);
    
    vec3 base = uHasTexture ? texture(uTexture0, fin.uv).rgb : uColor;
    
    float grid = step(0.95, fract(fin.worldPos.x * 20.0)) + 
                 step(0.95, fract(fin.worldPos.y * 20.0)) +
                 step(0.95, fract(fin.worldPos.z * 20.0));
    
    vec3 gridColor = vec3(0.0, 1.0, 1.0);
    vec3 color = mix(base * (0.2 + 0.8 * NdotL), gridColor, clamp(grid, 0.0, 1.0));
    
    outColor = vec4(color, 1.0);
}
"""

matrix_shader = """
#version 330 core

in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;

out vec4 outColor;

uniform float uTime;

float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
}

void main() {
    vec2 uv = fin.uv * 20.0;
    float t = uTime * 2.0;
    float chars = random(floor(uv) + floor(t));
    
    float brightness = step(0.7, chars) * (1.0 - fract(uv.y - t));
    vec3 color = vec3(0.0, brightness, 0.0);
    
    if (brightness > 0.8) {
        color = vec3(0.5, 1.0, 0.5);
    }
    
    outColor = vec4(color, 1.0);
}
"""

disco_shader = """
#version 330 core

in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;

out vec4 outColor;

uniform float uTime;

void main() {
    vec3 N = normalize(fin.normal);
    vec3 faceted = floor(N * 10.0) / 10.0;
    float hue = fract(length(faceted) + uTime * 0.3);
    
    vec3 color;
    if (hue < 0.166) {
        color = mix(vec3(1,0,0), vec3(1,1,0), hue * 6.0);
    } else if (hue < 0.333) {
        color = mix(vec3(1,1,0), vec3(0,1,0), (hue - 0.166) * 6.0);
    } else if (hue < 0.5) {
        color = mix(vec3(0,1,0), vec3(0,1,1), (hue - 0.333) * 6.0);
    } else if (hue < 0.666) {
        color = mix(vec3(0,1,1), vec3(0,0,1), (hue - 0.5) * 6.0);
    } else if (hue < 0.833) {
        color = mix(vec3(0,0,1), vec3(1,0,1), (hue - 0.666) * 6.0);
    } else {
        color = mix(vec3(1,0,1), vec3(1,0,0), (hue - 0.833) * 6.0);
    }
    
    float sparkle = step(0.98, fract(sin(dot(floor(N * 50.0), vec2(12.9898, 78.233))) * 43758.5453 + uTime));
    color = mix(color, vec3(1.0), sparkle);
    
    outColor = vec4(color, 1.0);
}
"""

negative_shader = """
#version 330 core
in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;
out vec4 outColor;
uniform sampler2D uTexture0;
uniform bool      uHasTexture;
uniform vec3      uColor;
void main() {
    vec3 base = uHasTexture ? texture(uTexture0, fin.uv).rgb : uColor;
    outColor = vec4(1.0 - base, 1.0);
}
"""

magma_shader = """
#version 330 core
in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;
out vec4 outColor;
uniform vec3      uLightPos;
uniform sampler2D uTexture0;
uniform bool      uHasTexture;
uniform vec3      uColor;
vec3 ramp(float t) {
    return mix(vec3(0.05, 0.0, 0.1), vec3(1.0, 0.6, 0.0), clamp(t, 0.0, 1.0));
}
void main() {
    vec3 N = normalize(fin.normal);
    vec3 L = normalize(uLightPos - fin.worldPos);
    float d = max(dot(N, L), 0.0);
    vec3 base = uHasTexture ? texture(uTexture0, fin.uv).rgb : uColor;
    vec3 col = ramp(pow(d, 0.6)) * base;
    outColor = vec4(col, 1.0);
}
"""

sepia_shader = """
#version 330 core
in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;
out vec4 outColor;
uniform sampler2D uTexture0;
uniform bool      uHasTexture;
uniform vec3      uColor;
void main() {
    vec3 c = uHasTexture ? texture(uTexture0, fin.uv).rgb : uColor;
    vec3 sep = vec3(
        dot(c, vec3(0.393, 0.769, 0.189)),
        dot(c, vec3(0.349, 0.686, 0.168)),
        dot(c, vec3(0.272, 0.534, 0.131))
    );
    outColor = vec4(sep, 1.0);
}
"""

normal_visualization_shader = """
#version 330 core
in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;
out vec4 outColor;
void main() {
    vec3 n = normalize(fin.normal) * 0.5 + 0.5;
    outColor = vec4(n, 1.0);
}
"""

unlit_shader = """
#version 330 core
in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;
out vec4 outColor;
uniform sampler2D uTexture0;
uniform bool      uHasTexture;
uniform vec3      uColor;
void main() {
    vec3 base = uHasTexture ? texture(uTexture0, fin.uv).rgb : uColor;
    outColor = vec4(base, 1.0);
}
"""