import { sleep } from 'k6';
import http from 'k6/http';
import { SharedArray } from 'k6/data';
import { check, fail } from 'k6';

const csvData = new SharedArray('data', function () {
    return open('./data.csv').split('\n').filter(line => !line.startsWith('#') && line.trim() !== '').slice(1);
});

// set this to sn_httpd instance
const SERVER = "http://localhost:8080/";

function getRandomRow() {
    const randomIndex = Math.floor(Math.random() * csvData.length);
    return csvData[randomIndex].split(',');
}

export default function () {
    try {
        const row = getRandomRow();
        const name = row[1];
        const address = row[2];

        const url = `${SERVER}${address}/${name}`;

        const start = new Date().getTime();
        const response = http.get(url);
        const end = new Date().getTime();
        const duration = end - start;
        const downloadSize = parseInt(response.headers['Content-Length']) || 0;

        if (downloadSize < 1024) {
            console.error(`Name: ${name}, Duration: ${duration} ms, Download Size: ${downloadSize} bytes - Error: Download size is less than 1KB`);
            response.status = 501;
        }

        if (response.status !== 200 && response.status !== 501) {
            throw new Error(`Request failed with status: ${response.status}`);
        }

        check(response, {
            'status is 200': (r) => r.status === 200,
        });

        sleep(1);
    } catch (error) {
        console.error(`Error: ${error.message}`);
    }
}
