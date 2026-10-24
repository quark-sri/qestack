# Performance testing recipe: TypeScript and JavaScript

Common choice: k6 (scripts in JavaScript or TypeScript, run by the k6 binary). Artillery is another option. For frontend page speed, use Lighthouse or browser performance metrics. Use what the project already has.

## k6 script with an open workload and thresholds

```js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    checkout: {
      executor: 'ramping-arrival-rate',          // open model: a target arrival rate
      startRate: 1, timeUnit: '1s', preAllocatedVUs: 100, maxVUs: 500,
      stages: [{ target: 50, duration: '5m' }, { target: 50, duration: '15m' }],
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<400', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
    checks: ['rate>0.99'],
  },
};

export default function () {
  const res = http.post(`${__ENV.BASE_URL}/orders`, JSON.stringify({ sku: `SKU-${__VU}-${__ITER}`, quantity: 1 }),
    { headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${__ENV.TOKEN}` } });
  check(res, { 'created': (r) => r.status === 201 });
  sleep(2 + Math.random() * 3);                  // think time
}
```

Run with `k6 run checkout.js -e BASE_URL=... -e TOKEN=...`. A failed threshold gives a non-zero exit code, so it can be a pipeline gate.
