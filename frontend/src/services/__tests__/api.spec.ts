import { describe, it, expect, vi } from 'vitest';
import { apiService } from '../api';
import axios from 'axios';

vi.mock('axios'); // Simulamos axios para no hacer peticiones reales

describe('apiService', () => {
  it('debe guardar el token en localStorage al hacer login', async () => {
    const mockToken = { access_token: 'fake_token', token_type: 'bearer' };
    (axios.create().post as any).mockResolvedValue({ data: mockToken });

    const data = await apiService.login('user', 'pass');
    
    expect(data.access_token).toBe('fake_token');
  });
});