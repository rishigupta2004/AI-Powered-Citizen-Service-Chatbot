import React from "react";

interface LogoProps {
  className?: string;
  size?: "sm" | "md" | "lg" | "xl";
  showText?: boolean;
  variant?: "color" | "white" | "navy";
}

export function Logo({
  className = "",
  size = "md",
  showText = true,
  variant = "color",
}: LogoProps) {
  const sizes = {
    sm: { emblem: 32, text: "text-lg" },
    md: { emblem: 40, text: "text-xl" },
    lg: { emblem: 56, text: "text-2xl" },
    xl: { emblem: 72, text: "text-3xl" },
  };

  const colors = {
    color: {
      saffron: "#FF9933",
      white: "#FFFFFF",
      green: "#138808",
      navy: "#000080",
      text: "text-[#000080]",
    },
    white: {
      saffron: "#FFFFFF",
      white: "#FFFFFF",
      green: "#FFFFFF",
      navy: "#FFFFFF",
      text: "text-white",
    },
    navy: {
      saffron: "#000080",
      white: "#000080",
      green: "#000080",
      navy: "#000080",
      text: "text-[#000080]",
    },
  };

  const { emblem, text: textSize } = sizes[size];
  const colorScheme = colors[variant];

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* Ashoka Chakra Inspired Emblem */}
      <svg
        width={emblem}
        height={emblem}
        viewBox="0 0 100 100"
        className="flex-shrink-0"
      >
        {/* Outer circle - Saffron */}
        <circle
          cx="50"
          cy="50"
          r="48"
          fill={colorScheme.saffron}
          opacity="0.1"
        />

        {/* Middle circle - Navy */}
        <circle
          cx="50"
          cy="50"
          r="42"
          fill="none"
          stroke={colorScheme.navy}
          strokeWidth="2"
        />

        {/* Inner Chakra - 24 spokes representing 24 hours of service */}
        <g transform="translate(50, 50)">
          {/* Center circle */}
          <circle cx="0" cy="0" r="6" fill={colorScheme.navy} />

          {/* 24 spokes */}
          {Array.from({ length: 24 }).map((_, i) => {
            const angle = (i * 360) / 24;
            const radian = (angle * Math.PI) / 180;
            const x1 = Math.cos(radian) * 8;
            const y1 = Math.sin(radian) * 8;
            const x2 = Math.cos(radian) * 35;
            const y2 = Math.sin(radian) * 35;

            return (
              <line
                key={i}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke={colorScheme.navy}
                strokeWidth="1.5"
                strokeLinecap="round"
              />
            );
          })}

          {/* Decorative dots at spoke ends */}
          {Array.from({ length: 24 }).map((_, i) => {
            const angle = (i * 360) / 24;
            const radian = (angle * Math.PI) / 180;
            const x = Math.cos(radian) * 35;
            const y = Math.sin(radian) * 35;

            return (
              <circle
                key={`dot-${i}`}
                cx={x}
                cy={y}
                r="2"
                fill={
                  i % 3 === 0
                    ? colorScheme.saffron
                    : i % 3 === 1
                      ? colorScheme.green
                      : colorScheme.navy
                }
              />
            );
          })}
        </g>

        {/* Outer decorative ring */}
        <circle
          cx="50"
          cy="50"
          r="48"
          fill="none"
          stroke={colorScheme.navy}
          strokeWidth="1.5"
          strokeDasharray="3 3"
        />
      </svg>

      {/* Text */}
      {showText && (
        <div className="flex flex-col">
          <div
            className={`font-bold ${textSize} leading-none ${colorScheme.text}`}
          >
            सेवा सिंधु
          </div>
          <div
            className={`text-xs ${colorScheme.text} opacity-80 font-medium tracking-wide`}
          >
            SEVA SINDHU
          </div>
        </div>
      )}
    </div>
  );
}