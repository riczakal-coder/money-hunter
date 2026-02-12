import axios from 'axios';

// 1. Deal 인터페이스
export interface Deal {
    id: number;
    site_name: string;
    title: string;
    url: string;
    price: string | null;
    is_sent: boolean;
    created_at: string;
}

// 2. API Response 타입
interface DealResponse {
    count: number;
    deals: Deal[];
}

// 3. Axios Instance
const api = axios.create({
    baseURL: 'http://5.78.131.126:8000', // 서버 IP
    timeout: 5000,
});

// 4. 데이터 Fetching 함수
export const fetchDeals = async (): Promise<Deal[]> => {
    try {
        const { data } = await api.get<DealResponse>('/deal/latest');
        return data.deals;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};
