import { test } from '../helpers/fixtures'
import { shoot } from '../helpers/screenshot'
import { env } from '../helpers/env'
import { login, expectPerson } from '../helpers/gramps'

const user = env('PLAYWRIGHT_DEVICE_USER')
const password = env('PLAYWRIGHT_DEVICE_PASSWORD')

test('person survives the upgrade', async ({ page }) => {
  await login(page, user, password)
  await shoot(page, 'main-after-upgrade')
  await expectPerson(page, 'Upgrade', 'Survivor')
  await shoot(page, 'person-after-upgrade')
})
