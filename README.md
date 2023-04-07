﻿# tcpfunnel

This repo contains code for creating a TCP Funnel. (Not guaranteed to work)

The server application can recieve a client and funnel data to the client application which will forward that data to a server.

This application basically allows for proxy port forwarding, where if a server is running in a restricted network domain that has not port forwared the server ports. One can run the server application in a different network domain, port forwarding the client and funnel ports, and then run the client application in the same network domain as the target server in the restricted network domain. This will open up an addressable server to the internet and will funnel the traffic to the actual target server in the restricted network. Note, this will dramatically increase latency.

SSL and HTTPS not supported. However, the funnel traffic is encrypted with AES.
