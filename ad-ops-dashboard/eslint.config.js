import globals from "globals";
import js from "@eslint/js";
import jsxA11y from "eslint-plugin-jsx-a11y";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { settings: { react: { version: "18.3" } } },
  { ignores: [".vite", "coverage", "dist", "node_modules"] },
  {
    extends: [
      js.configs.recommended,
      ...tseslint.configs.strictTypeChecked,
      ...tseslint.configs.stylisticTypeChecked,
    ],
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        project: ["./tsconfig.node.json", "./tsconfig.app.json"],
        tsconfigRootDir: import.meta.dirname,
        // We're currently using typescript 5.6.2 and typescript-eslint supports up to 5.6.0.ß
        // The warning below is currently disabled since that seems a safe enough version difference.
        // We may want to re-enable this once typescript-eslint catches up, which we can check here:
        // https://typescript-eslint.io/users/dependency-versions/#typescript
        warnOnUnsupportedTypeScriptVersion: false,
      },
    },
    plugins: {
      react,
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      "jsx-ally": jsxA11y,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
      ...react.configs.recommended.rules,
      ...react.configs["jsx-runtime"].rules,
      "@typescript-eslint/no-misused-promises": [
        "error",
        {
          "checksVoidReturn": false
        },
      ],
    },
  },
);
