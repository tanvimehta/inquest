README LAB3:
A. PUBLIC IP : http://54.172.218.21/ 
NOTE: The database was created by crawling with a depth=2 in order to demonstrate pagination

B. Benchmarks: 
1. The maximum continuous instructions without drops is 13
	ab -n 1000 -c 13 http://54.172.218.21/results?keywords=hello+&search=Search

2. Maximum Requests per cycle achieved with the above commands 
	Requests per second:    10.43 [#/sec] (mean)

3. Response Times: 
99 percentile = 11368 ms
average response time = 1212 ms


4. The following numbers are daily averages
(a) CPU Utilization 4.99 percent
(b) Memory : free : 130236 Buff 93912 Cache 245032 
(c) Disk IO = 0.2 KB/s  
(d) Network In = 13000 Bytes 
    Network Out = 26000 Bytes 

C. Explaination

As we see from the Benchamarks, the number of concurrent requests without loss has gone down from 20 to 13. Also, the average response time has gone up from 71 ms to 1212 ms. The requests per second stays almost the same. On top of this, the CPU utilization has increased from 4.07 % to 4.99 %. But the Network In and Network out has decreased. 
The increased latency for each request is due to accessing the persistent storage required to do the search. This increases the average response time and it results in fewer concurrent requests. 
The decease in Network bytes is due to the fact that we don’t print the history table and word table for each result. 


