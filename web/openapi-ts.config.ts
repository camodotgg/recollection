import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  client: '@hey-api/client-axios',
  input: 'openapi.json',
  output: {
    path: 'src/api/generated',
    format: 'prettier',
    lint: 'eslint',
  },
  plugins: [
    '@hey-api/schemas',
    '@hey-api/sdk',
    {
      enums: 'javascript',
      name: '@hey-api/typescript',
    },
  ],
});
