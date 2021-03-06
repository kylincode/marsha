import { flushAllPromises } from '../../testSetup';

import { shallow } from 'enzyme';
import fetchMock from 'fetch-mock';
import * as React from 'react';

const makeFormData = jest.fn().mockReturnValue('form data body');
jest.doMock('../../utils/makeFormData/makeFormData', () => ({ makeFormData }));

jest.doMock('react-router-dom', () => ({
  Redirect: () => {},
}));

import { Video } from '../../types/Video';
import { VideoForm } from './VideoForm';

describe('VideoForm', () => {
  const video = {
    description: '',
    id: 'ab42',
    status: 'no_ready',
    title: '',
  } as Video;

  afterEach(fetchMock.restore);

  it('renders the form by default', () => {
    fetchMock.mock('/api/videos/ab42/upload-policy/', {});
    const wrapper = shallow(<VideoForm jwt={'some_token'} video={video} />);

    expect(wrapper.html()).toContain('Create a new video');
  });

  it('gets the policy from the API and uses it to upload the file', async () => {
    // 1st call: home API call to get the AWS upload policy
    fetchMock.mock(
      '/api/videos/ab42/upload-policy/',
      JSON.stringify({
        acl: 'policy##acl',
        bucket: 'good-ol-bucket',
        key: 'policy##key',
        policy: 'policy##policy',
        s3_endpoint: 's3.aws.example.com',
        x_amz_algorithm: 'policy##x_amz_algorithm',
        x_amz_credential: 'policy##x_amz_credential',
        x_amz_date: 'policy##x_amz_date',
        x_amz_signature: 'policy##x_amz_signature',
      }),
    );

    // 2nd call: AWS bucket multipart POST to upload the file
    fetchMock.mock('https://s3.aws.example.com/good-ol-bucket', {});

    const wrapper = shallow(<VideoForm jwt={'some_token'} video={video} />);
    const componentInstance = wrapper.instance() as VideoForm;

    expect(fetchMock.lastCall()).toEqual([
      '/api/videos/ab42/upload-policy/',
      { headers: { Authorization: 'Bearer some_token' } },
    ]);

    await flushAllPromises();

    componentInstance.setState({
      file: { stub: 'file', type: 'video/mp4' } as any,
    });
    componentInstance.upload();

    expect(makeFormData).toHaveBeenCalledWith(
      ['key', 'policy##key'],
      ['acl', 'policy##acl'],
      ['Content-Type', 'video/mp4'],
      ['X-Amz-Credential', 'policy##x_amz_credential'],
      ['X-Amz-Algorithm', 'policy##x_amz_algorithm'],
      ['X-Amz-Meta-Jwt', 'some_token'],
      ['X-Amz-Date', 'policy##x_amz_date'],
      ['Policy', 'policy##policy'],
      ['X-Amz-Signature', 'policy##x_amz_signature'],
      ['file', { stub: 'file', type: 'video/mp4' }],
    );
    expect(fetchMock.lastCall()).toEqual([
      'https://s3.aws.example.com/good-ol-bucket',
      { body: 'form data body', method: 'POST' },
    ]);
  });

  it('redirects to /errors/policy when it fails to get the policy', async () => {
    fetchMock.mock('/api/videos/ab42/upload-policy/', {
      throws: 'invalid policy',
    });
    const wrapper = shallow(<VideoForm jwt={'some_token'} video={video} />);

    expect(wrapper.name()).toEqual('Redirect');
    expect(wrapper.prop('push')).toBeTruthy();
    expect(wrapper.prop('to')).toEqual('/errors/policy');
  });

  it('redirects to /errors/upload when it fails to upload the file', async () => {
    // 1st call: home API call to get the AWS upload policy
    fetchMock.mock(
      '/api/videos/ab42/upload-policy/',
      JSON.stringify({
        acl: 'policy##acl',
        bucket: 'good-ol-bucket',
        key: 'policy##key',
        policy: 'policy##policy',
        s3_endpoint: 's3.aws.example.com',
        x_amz_algorithm: 'policy##x_amz_algorithm',
        x_amz_credential: 'policy##x_amz_credential',
        x_amz_date: 'policy##x_amz_date',
        x_amz_signature: 'policy##x_amz_signature',
      }),
    );

    // 2nd call: AWS bucket multipart POST to upload the file
    fetchMock.mock('https://s3.aws.example.com/good-ol-bucket', {
      throws: 'failed to upload file',
    });

    const wrapper = shallow(<VideoForm jwt={'some_token'} video={video} />);
    const componentInstance = wrapper.instance() as VideoForm;
    await flushAllPromises();
    componentInstance.setState({
      file: { stub: 'file', type: 'video/mp4' } as any,
    });
    componentInstance.upload();

    expect(wrapper.name()).toEqual('Redirect');
    expect(wrapper.prop('push')).toBeTruthy();
    expect(wrapper.prop('to')).toEqual('/errors/upload');
  });
});
