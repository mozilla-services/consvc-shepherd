/** @type {import('ts-jest').JestConfigWithTsJest} **/
export default {
  roots: ["<rootDir>/src"],
  collectCoverage: true,
  collectCoverageFrom: [
    "src/**/*.{js,jsx,ts,tsx}",
    "!src/**/*.d.ts",
    "!src/__mocks__/**",
  ],
  // Not ready for this yet, but let's get there soon
  // coverageThreshold: {
  //   global: {
  //     lines: 95,
  //   },
  // },
  testEnvironment: "jest-environment-jsdom",
  modulePaths: ["<rootDir>/src"],
  transform: {
    "^.+\\.(t|j)sx?$": [
      "@swc/jest",
      {
        jsc: {
          transform: {
            react: {
              runtime: "automatic",
            },
          },
          experimental: {
            plugins: [["swc-plugin-import-meta-env", {}]],
          },
        },
      },
    ],
  },
  transformIgnorePatterns: [
    "[/\\\\]node_modules[/\\\\].+\\.(js|jsx|mjs|cjs|ts|tsx)$",
  ],
  modulePaths: ["<rootDir>/src"],
  moduleNameMapper: {
    "^.+.(css|styl|less|sass|scss|png|jpg|ttf|woff|woff2)$":
      "jest-transform-stub",
  },
  moduleFileExtensions: [
    "tsx",
    "ts",
    "web.js",
    "js",
    "web.ts",
    "web.tsx",
    "json",
    "web.jsx",
    "jsx",
    "node",
  ],
  resetMocks: true,
};
