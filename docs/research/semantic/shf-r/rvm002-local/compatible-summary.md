| n | Model | Samples | Median ms | Range ms | Allocations | Requested bytes | Peak extra bytes | Steps |
|---:|---|---:|---:|---|---:|---:|---:|---:|
| 16 | compatible | 3 | 0.159 | 0.143–0.184 | 380 | 71693 | 13469 | 243 |
| 16 | prototype | 3 | 0.147 | 0.139–0.202 | 528 | 25517 | 12261 | 243 |
| 128 | compatible | 3 | 2.040 | 1.888–2.056 | 2780 | 3956749 | 64053 | 1811 |
| 128 | prototype | 3 | 1.061 | 1.051–1.088 | 4426 | 165317 | 46669 | 1811 |
| 1024 | compatible | 3 | 138.855 | 128.522–173.072 | 24668 | 254205965 | 483381 | 14355 |
| 1024 | prototype | 3 | 14.808 | 13.741–15.832 | 41028 | 1608797 | 319413 | 14355 |
| 4096 | compatible | 3 | 1907.235 | 1812.545–2499.822 | 106588 | 4070236173 | 1921077 | 57363 |
| 4096 | prototype | 3 | 51.140 | 48.131–82.608 | 180288 | 7383917 | 1253541 | 57363 |
| 8192 | compatible | 3 | 6796.697 | 6700.113–7612.062 | 221276 | 16283000845 | 3838005 | 114707 |
| 8192 | prototype | 3 | 72.500 | 69.871–78.145 | 376894 | 15739637 | 2498845 | 114707 |
| 16384 | compatible | 3 | 30089.401 | 30056.445–31083.181 | 458844 | 65136156685 | 7671861 | 229395 |
| 16384 | prototype | 3 | 171.196 | 166.852–192.240 | 786492 | 33434237 | 4989333 | 229395 |
| 32768 | prototype | 1 | 332.019 | 332.019–332.019 | 1638458 | 70789637 | 9970189 | 458771 |

compatible descriptive log-log slope on 1024–16384: 1.925.

prototype descriptive log-log slope on 1024–16384: 0.852.

Compatible baseline 32768: INCOMPLETE at 90 seconds. No extension/retry. Largest candidate matched-series sample count is one; earlier three candidate samples remain separate raw evidence.