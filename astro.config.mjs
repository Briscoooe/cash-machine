import { defineConfig } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';

export default defineConfig({
  output: 'server',
  adapter: cloudflare({
    bindings: {
      DB: { type: 'd1', databaseName: 'cash-machine', databaseId: 'eeb98259-0e2f-44a0-8683-470f3d614e3c' }
    }
  })
});
