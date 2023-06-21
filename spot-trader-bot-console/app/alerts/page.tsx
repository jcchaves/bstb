'use client';

import { useEffect, useRef, useState } from "react"
import { StatProps } from "../types/core/stat"

export default function Alerts() {

    const wsClientRef = useRef<WebSocket | null>(null);
    const [wsConnecting, setWsConnecting] = useState<boolean>(false)

    const [stats, setStats] = useState<Array<StatProps>>([]);

    const addStat = (stat: StatProps) => {
        setStats((prevStats) => [stat, ...prevStats].slice(0, 5));
    };

    useEffect(() => {
        console.log("Alerts page mounted...")
        if (wsConnecting) {
            return
        }
        if (!wsClientRef.current) {
            const webSocket = new WebSocket("ws://localhost:8080/ws")

            wsClientRef.current = webSocket

            webSocket.onopen = (event) => {
                console.log("Connected to stats stream...")
            };

            webSocket.onmessage = function (event) {
                const newStat: StatProps = JSON.parse(event.data);
                try {
                    addStat(newStat);
                } catch (err) {
                    console.log(err);
                }
            }

            webSocket.onclose = (event) => {
                console.log("Attempting reconnection...")
                setWsConnecting(true);
                setTimeout(() => setWsConnecting(false), 5000);
            }
            return () => {
                wsClientRef.current = null
                webSocket.close()
            }
        }
    }, [wsConnecting])


    //map the first 5 bids
    const statsList = stats.map((stat, i) => {
        return (
            <tr key={i}>
                <th scope="row">{i}</th>
                <td>{stat.symbol}</td>
                <td>{stat.price}</td>
                <td>{stat.price15MinsAgo}</td>
                <td>{stat.percentDiff15Mins}%</td>
                <td>{stat.price2MinsAgo}</td>
                <td>{stat.percentDiff2Mins}%</td>
            </tr>

        );
    });



    return (
        <div className="container">
            <h1>Ticker price changes</h1>
            <table class="table">
                <thead>
                    <tr>
                        <th scope="col">#</th>
                        <th scope="col">Symbol</th>
                        <th scope="col">Price</th>
                        <th scope="col">Price 15 minutes ago</th>
                        <th scope="col">Percent diff. 15 minutes ago</th>
                        <th scope="col">Price 2 minutes ago</th>
                        <th scope="col">Percent diff. 2 minutes ago</th>
                    </tr>
                </thead>
                <tbody>
                    {statsList}
                </tbody>
            </table>
        </div>
    );
}