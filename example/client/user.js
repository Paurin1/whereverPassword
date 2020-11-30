UserData = {
    username: 'paurin',
    pin: '',
    password: 'zCF7Bre+zoiEf0vo1yGfyPnqZpQtBzbijFkAtmzP+bw=',
    aes_key: "6u0HcwdOsE7L8GsUkRBLgtX5/Uz5Hyf5",

    encryption: null
};

Rij.init(UserData['aes_key']);
UserData.encryption = Rij;