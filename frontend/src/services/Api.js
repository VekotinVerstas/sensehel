import axios from 'axios';
import _ from 'lodash';
import LocalStorageKeys from '../config/LocalStorageKeys';

const URL = 'http://127.0.0.1:8000/api/';

class Api {
  cache = {};

  constructor(baseUrl) {
    this.api = axios.create({
      baseURL: baseUrl,
      timeout: 5000
    });

    this.api.interceptors.response.use(
      response => response.data,
      error => {
        if (error.response.status === 401) {
          localStorage.clear();

          // Hacky-ish and ugly but works and quick
          window.alert('You have been logged out due to inactivity');
          window.location = '/login';
        }
        throw error;
      }
    );
  }

  async setToken(token) {
    this.api.interceptors.request.use(config => {
      config.headers.post.Authorization = `Token ${token}`; // eslint-disable-line
      config.headers.get.Authorization = `Token ${token}`; // eslint-disable-line
      config.headers.delete.Authorization = `Token ${token}`; // eslint-disable-line

      return config;
    });
  }

  async login(username, password) {
    try {
      const res = await this.api.post('login/', {
        username,
        password
      });

      localStorage.setItem(LocalStorageKeys.CURRENT_USER, JSON.stringify(res));
      await this.setToken((res || { token: '' }).token);
    } catch (e) {
      if (e.response.status === 400) {
        throw new Error('Incorrect username or password');
      }
      throw e;
    }
  }

  async getApartment() {
    if (!this.cache.apartment) {
      const res = await this.api.get('apartments/');
      if (!res.length) throw new Error('No apartment registered to you.');
      this.cache.apartment = res[0]; // eslint-disable-line
    }
    return this.cache.apartment;
  }

  async getAvailableServices() {
    return this.api.get('available-services/');
  }

  async  getServiceSubscriptions() {
    const res = await this.api.get('subscriptions/');
    localStorage.setItem(
      LocalStorageKeys.SUBSCRIBED_SERVICES,
      JSON.stringify(res)
    );

    return res;
  }

  addSubscribedService(id, apsenAttrIds, includeHistory) {
    return this.api.post('subscriptions/', {
      service: id,
      attributes: apsenAttrIds,
      include_history: includeHistory
    });
  }

  deleteSubscribedService(id) {
    return this.api.delete(`subscriptions/${id}/`);
  }

  async getSensorValues() {
    const apartment = await this.getApartment();
    return _.flatten(
      apartment.apartment_sensors.map(apsen =>
        _.filter(apsen.attributes, 'ui_type').map(
          ({
            description,
            uri,
            ui_type: uiType,
            value,
            updated_at: updatedAt
          }) => ({
              id: `${apsen.id}-${description.substr(0, 5)}`,
              name: apsen.sensor.description,
              identifier: apsen.identifier,
              uri,
              description,
              uiType,
              value,
              updatedAt
            })
        )
      )
    );
  }

  revokeApartment() {
    const currentUser = JSON.parse(
      localStorage.getItem(LocalStorageKeys.CURRENT_USER)
    );
    const ID = currentUser && currentUser.id;
    if (ID) return this.api.delete(`users/${ID}/`);

    throw new Error('User not logged in!');
  }
}

const API = new Api(URL);

export default API;
