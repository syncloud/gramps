import { test as base } from '@playwright/test'
import * as path from 'node:path'
import { shoot } from './screenshot'

export const test = base.extend({})

test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status === testInfo.expectedStatus) {
    return
  }
  console.log(`failure url: ${page.url()}`)
  const spec = path.basename(testInfo.file, '.spec.ts')
  await shoot(page, `failed-${spec}-line-${testInfo.line}`)
})

export { expect } from '@playwright/test'
