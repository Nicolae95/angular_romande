from rest_framework import serializers
from rest_auth.serializers import UserDetailsSerializer
from .models import *
from companies.models import *
from companies.serializers import *
from offers.utils.send_mail import py_mail


# def generate_email_content(obj):
#         context = {
#             "user": obj,
#         }
#         template = get_template('tool/mail/email-thanks.html')
#         email_content = template.render(context)
#         # print email_content
#         return email_content


class UserSerializer(UserDetailsSerializer):
    role = serializers.IntegerField(source="profile.role")
    fonction = serializers.IntegerField(source="profile.fonction")
    temp = serializers.CharField(source="profile.temp", required=False)
    signature = serializers.FileField(source="profile.signature", required=False)
    token = serializers.CharField(source="profile.token", required=False)
    sex = serializers.CharField(source="profile.sex", required=False)
    other_fonction = serializers.CharField(source="profile.other_fonction", required=False)
    log = serializers.DateTimeField(source="profile.log", required=False)
    crm_id = serializers.IntegerField(source="profile.crm_id", required=False)
    per_pag = serializers.IntegerField(source="profile.per_pag", required=False)

    class Meta(UserDetailsSerializer.Meta):
        fields = ['pk', 'username', 'email', 'first_name', 'signature', 'fonction', 'last_name'] + \
        [f.name for f in Profile._meta.get_fields()]
        del fields[fields.index('user')]
        del fields[fields.index('auth')]
        del fields[fields.index('last_auth')]
        read_only_fields = ('token', 'temp', 'per_pag')


    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)
        profile = instance.profile
        p_info = model_meta.get_field_info(profile)

        for attr, value in validated_data.items():
            if attr == 'profile':
                for attr2, value2 in value.items():
                    setattr(profile, attr2, value2)
            elif attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        profile.save()
        return instance


class UserClientSerializer(UserDetailsSerializer):
    role = serializers.IntegerField(source="profile.role")
    fonction = serializers.IntegerField(source="profile.fonction")
    temp = serializers.CharField(source="profile.temp", required=False)
    token = serializers.CharField(source="profile.token", required=False)
    email = serializers.EmailField()
    other_fonction = serializers.CharField(source="profile.other_fonction", required=False)
    sex = serializers.CharField(source="profile.sex", required=False)
    signature = serializers.FileField(source="profile.signature", required=False)
    crm_id = serializers.IntegerField(source="profile.crm_id", required=False)
    per_pag = serializers.IntegerField(source="profile.per_pag", required=False)

    class Meta(UserDetailsSerializer.Meta):
        fields = ['pk', 'username', 'email',
                  'first_name', 'last_name', 'role', 'token', 'fonction', 'temp', 'sex', 'signature', 'crm_id', 'per_pag', 'other_fonction']
        read_only_fields = ('token', 'temp', 'signature', 'per_pag')
        extra_kwargs = {'crm_id': {'allow_null': True, 'allow_blank': True, 'required': False}}



    def create(self, validated_data):
        print validated_data
        user = User(
            username = validated_data['username'],
            email = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            )
        if int(validated_data['profile']['role']) == 1:
            # user.is_staff = True
            user.is_admin = True
            user.is_superuser = True
        # user.set_password(validated_data['password'])
        user.save()
        profile = Profile.objects.get(user = user)
        profile.role = int(validated_data['profile']['role'])
        profile.fonction = int(validated_data['profile']['fonction'])
        profile.sex = validated_data['profile']['sex']
        try:
            profile.crm_id = int(validated_data['profile']['crm_id'])
        except:
            print('no crm')
        profile.other_fonction = validated_data['profile']['other_fonction']
        profile.save()
        return user

    def update(self, instance, validated_data):
        print 'validated_data', validated_data
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        # if not validated_data['signature']:
        #     instance.signature = validated_data.get('signature', None)
        # if validated_data['password'] != '0':
        #     instance.set_password(validated_data['password'])
        instance.save()
        profile = Profile.objects.filter(user = instance)
        profile.update(role=int(validated_data['profile']['role']))
        profile.update(fonction=int(validated_data['profile']['fonction']))
        profile.update(sex=validated_data['profile']['sex'])
        try:
            profile.update(crm_id=int(validated_data['profile']['crm_id']))
        except:
            print('no crm')
        profile.update(other_fonction=validated_data['profile']['other_fonction'])
        return instance


class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ('id', 'role', 'token', 'temp', 'user', 'sex', 'crm_id', 'per_pag')


class ClientPassSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('id', 'temp')
