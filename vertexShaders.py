vertex_shader = """
#version 330 core

layout (location=0) in vec3 inPosition;
layout (location=1) in vec2 inTexCoord;
layout (location=2) in vec3 inNormal;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

out VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} vout;

void main() {
    vec4 wpos = modelMatrix * vec4(inPosition, 1.0);
    vout.worldPos = wpos.xyz;
    vout.normal = mat3(modelMatrix) * inNormal;
    vout.uv = inTexCoord;
    gl_Position = projectionMatrix * viewMatrix * wpos;
}
"""

water_shader = """
#version 330 core

layout (location=0) in vec3 inPosition;
layout (location=1) in vec2 inTexCoord;
layout (location=2) in vec3 inNormal;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float uTime;

out VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} vout;

void main() {
    vec3 p = inPosition;
    
    float wave1 = sin(p.x * 3.0 + uTime * 2.0) * 0.04;
    float wave2 = cos(p.z * 4.0 + uTime * 1.5) * 0.03;
    float wave3 = sin((p.x + p.z) * 2.5 + uTime * 2.5) * 0.025;
    
    p.y += wave1 + wave2 + wave3;
    
    vec4 wpos = modelMatrix * vec4(p, 1.0);
    vout.worldPos = wpos.xyz;
    vout.normal = mat3(modelMatrix) * inNormal;
    vout.uv = inTexCoord;
    gl_Position = projectionMatrix * viewMatrix * wpos;
}
"""

twist_shader = """
#version 330 core

layout (location=0) in vec3 inPosition;
layout (location=1) in vec2 inTexCoord;
layout (location=2) in vec3 inNormal;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float uTime;

out VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} vout;

void main() {
    vec3 p = inPosition;
    
    float twistAmount = uTime + p.y * 2.0;
    float c = cos(twistAmount);
    float s = sin(twistAmount);
    
    mat2 rotation = mat2(c, -s, s, c);
    p.xz = rotation * p.xz;
    
    vec4 wpos = modelMatrix * vec4(p, 1.0);
    vout.worldPos = wpos.xyz;
    
    vec3 n = inNormal;
    n.xz = rotation * n.xz;
    vout.normal = mat3(modelMatrix) * n;
    
    vout.uv = inTexCoord;
    gl_Position = projectionMatrix * viewMatrix * wpos;
}
"""

pulse_shader = """
#version 330 core

layout (location=0) in vec3 inPosition;
layout (location=1) in vec2 inTexCoord;
layout (location=2) in vec3 inNormal;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float uTime;

out VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} vout;

void main() {
    vec3 p = inPosition;
    
    float pulse = sin(uTime * 3.0) * 0.15 + 1.0;
    float distFromCenter = length(p);
    p *= (1.0 + (pulse - 1.0) * (1.0 - distFromCenter * 0.5));
    
    vec4 wpos = modelMatrix * vec4(p, 1.0);
    vout.worldPos = wpos.xyz;
    vout.normal = mat3(modelMatrix) * inNormal;
    vout.uv = inTexCoord;
    gl_Position = projectionMatrix * viewMatrix * wpos;
}
"""

explode_shader = """
#version 330 core

layout (location=0) in vec3 inPosition;
layout (location=1) in vec2 inTexCoord;
layout (location=2) in vec3 inNormal;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float uTime;

out VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} vout;

void main() {
    vec3 p = inPosition;
    
    float explosionAmount = sin(uTime * 2.0) * 0.3 + 0.3;
    p += inNormal * explosionAmount;
    
    vec4 wpos = modelMatrix * vec4(p, 1.0);
    vout.worldPos = wpos.xyz;
    vout.normal = mat3(modelMatrix) * inNormal;
    vout.uv = inTexCoord;
    gl_Position = projectionMatrix * viewMatrix * wpos;
}
"""

jelly_shader = """
#version 330 core

layout (location=0) in vec3 inPosition;
layout (location=1) in vec2 inTexCoord;
layout (location=2) in vec3 inNormal;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float uTime;

out VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} vout;

void main() {
    vec3 p = inPosition;
    
    float wobbleX = sin(uTime * 4.0 + p.y * 5.0) * 0.02;
    float wobbleZ = cos(uTime * 3.5 + p.y * 4.5) * 0.02;
    
    p.x += wobbleX * (1.0 + p.y);
    p.z += wobbleZ * (1.0 + p.y);
    
    vec4 wpos = modelMatrix * vec4(p, 1.0);
    vout.worldPos = wpos.xyz;
    vout.normal = mat3(modelMatrix) * inNormal;
    vout.uv = inTexCoord;
    gl_Position = projectionMatrix * viewMatrix * wpos;
}
"""

spike_shader = """
#version 330 core

layout (location=0) in vec3 inPosition;
layout (location=1) in vec2 inTexCoord;
layout (location=2) in vec3 inNormal;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float uTime;

out VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} vout;

float hash(vec3 p) {
    p = fract(p * 0.3183099 + 0.1);
    p *= 17.0;
    return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

void main() {
    vec3 p = inPosition;
    
    float spike = hash(floor(p * 20.0));
    float spikeAmount = spike * sin(uTime * 2.0 + spike * 6.28) * 0.2;
    
    if (spike > 0.7) {
        p += inNormal * spikeAmount;
    }
    
    vec4 wpos = modelMatrix * vec4(p, 1.0);
    vout.worldPos = wpos.xyz;
    vout.normal = mat3(modelMatrix) * inNormal;
    vout.uv = inTexCoord;
    gl_Position = projectionMatrix * viewMatrix * wpos;
}
"""

melt_shader = """
#version 330 core

layout (location=0) in vec3 inPosition;
layout (location=1) in vec2 inTexCoord;
layout (location=2) in vec3 inNormal;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float uTime;

out VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} vout;

void main() {
    vec3 p = inPosition;
    
    float meltFactor = max(0.0, p.y) * sin(uTime + p.x * 2.0) * 0.3;
    p.y -= meltFactor;
    p.xz *= 1.0 + meltFactor * 0.2;
    
    vec4 wpos = modelMatrix * vec4(p, 1.0);
    vout.worldPos = wpos.xyz;
    vout.normal = mat3(modelMatrix) * inNormal;
    vout.uv = inTexCoord;
    gl_Position = projectionMatrix * viewMatrix * wpos;
}
"""

fat_shader = """
#version 330 core

layout (location=0) in vec3 inPosition;
layout (location=1) in vec2 inTexCoord;
layout (location=2) in vec3 inNormal;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float uTime;

out VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} vout;

void main() {
    float inflation = 0.08 + sin(uTime * 2.0) * 0.03;
    vec3 p = inPosition + inNormal * inflation;
    
    vec4 wpos = modelMatrix * vec4(p, 1.0);
    vout.worldPos = wpos.xyz;
    vout.normal = mat3(modelMatrix) * inNormal;
    vout.uv = inTexCoord;
    gl_Position = projectionMatrix * viewMatrix * wpos;
}
"""

glitch_vertex_shader = """
#version 330 core

layout (location=0) in vec3 inPosition;
layout (location=1) in vec2 inTexCoord;
layout (location=2) in vec3 inNormal;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float uTime;

out VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} vout;

float random(float x) {
    return fract(sin(x) * 43758.5453);
}

void main() {
    vec3 p = inPosition;
    
    float glitchFreq = floor(uTime * 10.0);
    float glitch = step(0.95, random(glitchFreq + floor(p.y * 10.0)));
    
    p.x += glitch * (random(glitchFreq) - 0.5) * 0.3;
    p.z += glitch * (random(glitchFreq + 1.0) - 0.5) * 0.2;
    
    vec4 wpos = modelMatrix * vec4(p, 1.0);
    vout.worldPos = wpos.xyz;
    vout.normal = mat3(modelMatrix) * inNormal;
    vout.uv = inTexCoord;
    gl_Position = projectionMatrix * viewMatrix * wpos;
}
"""