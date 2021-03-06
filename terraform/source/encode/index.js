'use strict';

const AWS = require('aws-sdk');

exports.handler = (event, context, callback) => {
  console.log('Received event:', JSON.stringify(event, null, 2));

  const objectKey = event.Records[0].s3.object.key;

  if (objectKey.split('/').length != 4) {
    let error =
      'Source videos should be uploaded in a folder of the form ' +
      '"{playlist_id}/{video_id}/videos/{stamp}".' +
      'Source subtitles should be uploaded to a folder of the form ' +
      '"{playlist_id}/{video_id}/subtitles/{stamp}_{language}[_{has_closed_caption}]".';
    callback(error);
    return;
  }

  let params = {
    Role: process.env.MEDIA_CONVERT_ROLE,
    UserMetadata: {
      Bucket: event.Records[0].s3.bucket.name,
      ObjectKey: objectKey,
    },
    Settings: {
      AdAvailOffset: 0,
      Inputs: [
        {
          FilterEnable: 'AUTO',
          PsiControl: 'USE_PSI',
          FilterStrength: 0,
          DeblockFilter: 'DISABLED',
          DenoiseFilter: 'DISABLED',
          TimecodeSource: 'EMBEDDED',
          VideoSelector: {
            ColorSpace: 'FOLLOW',
          },
          AudioSelectors: {
            'Audio Selector 1': {
              Offset: 0,
              DefaultSelection: 'DEFAULT',
              ProgramSelection: 1,
            },
          },
          FileInput:
            's3://' + event.Records[0].s3.bucket.name + '/' + objectKey,
        },
      ],
      OutputGroups: [
        {
          CustomName: 'Video MP4 outputs',
          Name: 'File Group',
          OutputGroupSettings: {
            Type: 'FILE_GROUP_SETTINGS',
            FileGroupSettings: {
              Destination:
                's3://' + process.env.S3_DESTINATION_BUCKET + '/' + objectKey,
            },
          },
          Outputs: [
            {
              Preset: process.env.ENV_TYPE + '_marsha_video_mp4_144',
              NameModifier: '_144',
            },
            {
              Preset: process.env.ENV_TYPE + '_marsha_video_mp4_240',
              NameModifier: '_240',
            },
            {
              Preset: process.env.ENV_TYPE + '_marsha_video_mp4_480',
              NameModifier: '_480',
            },
            {
              Preset: process.env.ENV_TYPE + '_marsha_video_mp4_720',
              NameModifier: '_720',
            },
            {
              Preset: process.env.ENV_TYPE + '_marsha_video_mp4_1080',
              NameModifier: '_1080',
            },
          ],
        },
        {
          CustomName: 'Thumbnails outputs',
          Name: 'File Group',
          OutputGroupSettings: {
            Type: 'FILE_GROUP_SETTINGS',
            FileGroupSettings: {
              Destination:
                's3://' +
                process.env.S3_DESTINATION_BUCKET +
                '/' +
                objectKey.replace('/videos/', '/thumbnails/'),
            },
          },
          Outputs: [
            {
              Preset: process.env.ENV_TYPE + '_marsha_thumbnail_jpeg_144',
              NameModifier: '_thumbnail_144',
            },
            {
              Preset: process.env.ENV_TYPE + '_marsha_thumbnail_jpeg_240',
              NameModifier: '_thumbnail_240',
            },
            {
              Preset: process.env.ENV_TYPE + '_marsha_thumbnail_jpeg_480',
              NameModifier: '_thumbnail_480',
            },
            {
              Preset: process.env.ENV_TYPE + '_marsha_thumbnail_jpeg_720',
              NameModifier: '_thumbnail_720',
            },
            {
              Preset: process.env.ENV_TYPE + '_marsha_thumbnail_jpeg_1080',
              NameModifier: '_thumbnail_1080',
            },
          ],
        },
        {
          CustomName: 'Previews outputs',
          Name: 'File Group',
          OutputGroupSettings: {
            Type: 'FILE_GROUP_SETTINGS',
            FileGroupSettings: {
              Destination:
                's3://' +
                process.env.S3_DESTINATION_BUCKET +
                '/' +
                objectKey.replace('/videos/', '/previews/'),
            },
          },
          Outputs: [
            {
              Preset: process.env.ENV_TYPE + '_marsha_preview_jpeg_100',
              NameModifier: '_preview_100',
            },
          ],
        },
      ],
    },
  };

  new AWS.MediaConvert({ endpoint: process.env.MEDIA_CONVERT_END_POINT })
    .createJob(params)
    .promise()
    .then(data => {
      console.log(JSON.stringify(data, null, 2));
      callback(null, { Job: data.Job.Id });
    })
    .catch(error => callback(error));
};
