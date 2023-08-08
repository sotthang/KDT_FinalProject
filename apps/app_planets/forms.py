from django import forms

from .models import Planet, Post, Comment, Recomment, InappropriateWord, VoteTopic, TermsOfService
from taggit.forms import TagField


def validate_inappropriate_words(value):
    inappropriate_words = InappropriateWord.objects.values_list('word', flat=True)
    for word in inappropriate_words:
        if word in value:
            raise forms.ValidationError(f'부적절한 단어 ({word}) 이/가 포함되어 있습니다. 다시 작성해주세요.')

class PlanetForm(forms.ModelForm):
    class Meta:
        model = Planet
        fields = ('name', 'description', 'category', 'is_public', 'need_confirm', 'image', 'maximum_capacity',)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['name'].widget.attrs['placeholder'] = " "
        self.fields['name'].label = '<span class="text-white">행성 이름</span>'
        self.fields['name'].help_text = ''
        
        self.fields['description'].widget.attrs['placeholder'] = " "
        self.fields['description'].label = '<span class="text-white">행성 설명</span>'
        self.fields['description'].help_text = ''
        
        self.fields['category'].widget.attrs['placeholder'] = " "
        self.fields['category'].label = '<span class="text-white">카테고리</span>'
        self.fields['category'].help_text = ''
        
        self.fields['is_public'].label = '<span class="text-white">공개 여부</span>'
        self.fields['is_public'].help_text = ''

        self.fields['need_confirm'].label = '<span class="text-white">가입 방식</span>'
        self.fields['need_confirm'].help_text = ''
        
        self.fields['image'].label = '<span class="text-white">행성 사진</span>'
        self.fields['image'].help_text = ''
        
        self.fields['maximum_capacity'].label = '<span class="text-white">행성 최대 인원</span>'
        self.fields['maximum_capacity'].help_text = ''
        
        # labels = {
        #     'name': '행성 이름', 
        #     'description': '행성 설명', 
        #     'category': '카테고리', 
        #     'is_public': '공개 여부',
        #     'image': '행성 사진', 
        #     'maximum_capacity': '행성 최대 인원',
        #     'need_confirm': '가입 승인 필요'
        # }
    def clean_name(self):
        name = self.cleaned_data['name']
        validate_inappropriate_words(name)
        return name
    
    def clean_description(self):
        description = self.cleaned_data['description']
        validate_inappropriate_words(description)
        return description

class TermsOfServiceForm(forms.ModelForm):
    class Meta:
        model = TermsOfService
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['content'].widget.attrs['placeholder'] = " "
        self.fields['content'].label = '<span class="text-white">행성 이름</span>'
        self.fields['content'].help_text = ''

class PostForm(forms.ModelForm):
    tags         = TagField(required=False)

    class Meta:
        model = Post
        fields = ('content', 'image', 'tags',)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['content'].widget.attrs['class'] = 'bg-[#101013] text-white mt-1 block w-full rounded-lg'
        self.fields['content'].widget.attrs['placeholder'] = "작성 할 내용을 입력해 주세요."
        self.fields['content'].help_text = ''
        
        self.fields['image'].widget.attrs['class'] = 'bg-white text-black mt-1 block w-3/4'
        self.fields['image'].help_text = ''
        
        self.fields['tags'].widget.attrs['class'] = 'bg-[#101013] text-white mt-1 block rounded-md'
        self.fields['tags'].widget.attrs['placeholder'] = " "
        self.fields['tags'].help_text = ''


        
        # labels = {
        #     'content': '내용',
        #     'image': '사진',
        #     'tags': '태그',
        # }
    
    def clean_content(self):
        content = self.cleaned_data['content']
        validate_inappropriate_words(content)
        return content
    
    def clean_tags(self):
        tags = self.cleaned_data['tags']
        validate_inappropriate_words(tags)
        return tags
        

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        labels = {
            'content': '내용',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['content'].widget.attrs['class'] = 'bg-[#101013] text-white mt-1 block w-full rounded-lg'
        self.fields['content'].widget.attrs['placeholder'] = "작성 할 내용을 입력해 주세요."
        self.fields['content'].help_text = ''
    
    def clean_content(self):
        content = self.cleaned_data['content']
        validate_inappropriate_words(content)
        return content


class RecommentForm(forms.ModelForm):
    class Meta:
        model = Recomment
        fields = ('content',)
        labels = {
            'content': '내용',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['content'].widget.attrs['class'] = 'bg-[#101013] text-white mt-1 block w-full rounded-lg'
        self.fields['content'].widget.attrs['placeholder'] = "작성 할 내용을 입력해 주세요."
        self.fields['content'].help_text = ''
    
    def clean_content(self):
        content = self.cleaned_data['content']
        validate_inappropriate_words(content)
        return content

class VoteTopicForm(forms.ModelForm):
    class Meta:
        model = VoteTopic
        fields = ('title',)
        labels = {
            'title': '내용',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'bg-[#101013] text-white mt-1 block w-full rounded-lg',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['title'].required = False
        self.fields['title'].help_text = ''

        


