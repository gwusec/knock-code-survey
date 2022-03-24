from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator,MinLengthValidator

"""Custom MultiChoiceField with a Other to handle better validations"""
class MultiChoiceFieldOther(forms.MultipleChoiceField):

    def clean(self,value):
        data = super().to_python(value)
        self.validate(data)
        self.run_validators(data)
        return data

    def validate(self,values):
        if not values and self.required:
            raise ValidationError("Please select at least one of the options",code="required")
        for v in values:
            if len(v) == 0:
                raise ValidationError("Other selection needs to be described",code="other")
            for validator in self.validators:
                validator(v)


#Each form appears on a page of its own. Check out the templates for those
# pages, plus the template for rendering a radio button entry with bootstrap.

class DemographicForm(forms.Form):

    age = forms.ChoiceField(
        label="Select your age:",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("18-24","18-24"),
                 ("25-29","25-29"),
                 ("30-34","30-34"),
                 ("35-39","35-39"),
                 ("40-44","40-44"),
                 ("45-49","45-49"),
                 ("50-54","50-54"),
                 ("54-59","54-59"),
                 ("60-64","60-64"),
                 ("65+","65+"),
                 ("N","Prefer not to answer"))
    )
    
    gender = forms.ChoiceField(
        label="Select your gender:",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("F", "Female"),
                 ("M","Male"),
                 ("B", "Non-Binary/Third Gender"),
                 ("D", "Not Described Here"),
                 ("N", "Prefer Not to Say"))
    )

    handed = forms.ChoiceField(
        label="What is your dominant hand?",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("L","Left Handed"),
                 ("R","Right Handed"),
                 ("A","Ambidextrous"),
                 ("N", "Prefer Not to Say"))
    )

    locale = forms.ChoiceField(
        label="Where you live is best described as:",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("U","Urban"),
                 ("S","Suburban"),
                 ("R","Rural"),
                 ("N", "Prefer Not to Say"))
    )

    education = forms.ChoiceField(
        label="What is the highest degree or level of school you have completed?",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("some-high","Some high school"),
		 ("high","High school"),
		 ("some-college","Some college"),
		 ("trade","Trade, technical, or vocational training"),
		 ("assoc","Associate's Degree"),
		 ("bach","Bachelor's Degree"),
		 ("master","Master's Degree"),
		 ("professional","Professional degree"),
		 ("doctorate","Doctorate"),
		 ("N","Prefer not to say"))

    )

    attention = forms.ChoiceField(
        label="What is the shape of a red ball?",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("R","Red"),
                 ("B","Blue"),
                 ("S","Square"),
                 ("Round","Round"),
                 ("PNS", "Prefer Not to Say"))
    )

    tech = forms.ChoiceField(
        label="Which of the following best describes your educational background or job field?",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("tech","I have an education in, or work in, the field of computer science, computer engineering or IT."),
                 ("no-tech","I do not have an education in, nor do I work in, the field of computer science, computer engineering or IT."),
                 ("na","Prefer not to say"))

    )


class DeviceForm(forms.Form):
    num = forms.ChoiceField(
        label="How many mobile devices do you use regularly? (Including phones, but excluding tablet and laptops)",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("0","0"),
                 ("1","1"),
                 ("2","2"),
                 ("3","3"),
                 ("4","4+"),
                 ("N", "Prefer Not to Say"))

    )

    brand = MultiChoiceFieldOther(
        label="What brands of smartphone do you use? (Select all that apply)",
        required=True,
        validators=[MaxLengthValidator(16),MinLengthValidator(1)],
        widget=forms.CheckboxSelectMultiple(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("Apple","Apple"),
                 ("Samsung", "Samsung"),
                 ("LG","LG"),
                 ("Motorola","Motorola"),
                 ("Google","Google/Pixel/Nexus"),
                 ("Huawei","Huawei"),
                 ("ZTE","ZTE"),
                 ("N","I do not own a smartphone"),
                 ("","OTHER")) ### other fields must appear like this to have the text rendering
    )

    no = forms.ChoiceField(
        label="Select 'No' as the answer to this question.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("Y","Yes"),
                 ("N", "No"),
                 ("M", "Sometimes"),
                 ("A", "Always"))
    )
    
    # usage = MultiChoiceFieldOther(
    #     label="What activities do you typically use your smartphone for? (Select all that apply)",
    #     required=True,
    #     validators=[MaxLengthValidator(16),MinLengthValidator(1)],
    #     widget=forms.CheckboxSelectMultiple(attrs={"class":"form-check-input"}), #this is for bootstrap
    #     choices=(("finances","Personal Finances"),
    #              ("entertainment", "Entertainment/Games"),
    #              ("communication","Communication"),
    #              ("shopping","Shopping"),
    #              ("work","Work"),
    #              ("web","Web Browsing"),
    #              ("social","Social Media"),
    #              ("","OTHER")) ### other fields must appear like this to have the text rendering
    # )

    curlock = MultiChoiceFieldOther(
        label="Which method(s) do you use to lock your mobile device(s)? (select all that apply)",
        required=True,
        validators=[MaxLengthValidator(16),MinLengthValidator(1)],
        widget=forms.CheckboxSelectMultiple(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("4-PIN","4-Digit PIN"),
                 ("6-PIN","6-Digit PIN"),
                 ("long-PIN","Greater than 6-Digit PIN"),
                 ("pattern","Android Graphical Pattern"),
                 ("knock","LG Knock Codes"),
                 ("fingerprint","Fingerprint"),
                 ("face","Facial Recognition"),
                 ("none","None"),
                 ("","OTHER")) ### other fields must appear like this to have the text rendering
    )



class PostEntryForm(forms.Form):
    security = forms.ChoiceField(
        label="I feel this Knock Code provides adequate security for this scenario.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
		 ("A","Agree"),
		 ("NAND","Neither Agree Nor Disagree"),
		 ("D","Disagree"),
		 ("SD","Strongly Disagree"))
    )

    difficulty = forms.ChoiceField(
        label="It was difficult to choose this Knock Code.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
		 ("A","Agree"),
		 ("NAND","Neither Agree Nor Disagree"),
		 ("D","Disagree"),
		 ("SD","Strongly Disagree"))
    )


    strat_secure = forms.CharField(
        label="What strategy did you use to make your code <u>more secure</u>?",
        required=True,
        max_length=512,
        min_length=1,
        widget=forms.Textarea(attrs={"class":"form-control","rows":"5","cols":"8"}), #this is for bootstrap
    )

    # strat_secure = MultiChoiceFieldOther(
    #     label="What strategy did you use to make your code <u>more secure</u>? (Select all that apply)",
    #     required=True,
    #     validators=[MaxLengthValidator(256),MinLengthValidator(1)],
    #     widget=forms.CheckboxSelectMultiple(attrs={"class":"form-check-input"}), #this is for bootstrap
    #     choices=(("used-rep","Used repititions"),
    #              ("avoid-rep", "Avoided repetitions"),
    #              ("more-quad","Used more quadrants"),
    #              ("less-quad","Used fewer quadrants"),
    #              ("more-len","Used more knocks in my code"),
    #              ("less-len","Used fewer knocks in my code"),
    #              ("more-diag","Used more diagonals in my code"),
    #              ("less-diag","Used fewer diagonals in my code"),
    #              ("","OTHER")) ### other fields must appear like this to have the text rendering
    # )


    strat_remember = forms.CharField(
        label="What strategy did you use to make your code <u>more memorable</u>?",
        
        required=True,
        max_length=512,
        min_length=1,
        widget=forms.Textarea(attrs={"class":"form-control","rows":"5","cols":"8"}), #this is for bootstrap
    )

    # strat_remember = MultiChoiceFieldOther(
    #     label="What strategy did you use to make your code <u>more memorable</u>? (Select all that apply)",
    #     required=True,
    #     validators=[MaxLengthValidator(256),MinLengthValidator(1)],
    #     widget=forms.CheckboxSelectMultiple(attrs={"class":"form-check-input"}), #this is for bootstrap
    #     choices=(("used-rep","Used repititions"),
    #              ("avoid-rep", "Avoided repetitions"),
    #              ("more-quad","Used more quadrants"),
    #              ("less-quad","Used fewer quadrants"),
    #              ("more-len","Used more knocks in my code"),
    #              ("less-len","Used fewer knocks in my code"),
    #              ("more-diag","Used more diagonals in my code"),
    #              ("less-diag","Used fewer diagonals in my code"),
    #              ("","OTHER")) ### other fields must appear like this to have the text rendering
    # )


class SecurityForm(forms.Form):
    secure = forms.ChoiceField(
        label="Knock Codes are a secure authenticator.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
                 ("A","Agree"),
                 ("NAND","Neither Agree Nor Disagree"),
                 ("D","Disagree"),
                 ("SD","Strongly Disagree"))
    )

    pin = forms.ChoiceField(
        label="Knock Codes are more secure than PIN codes.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
                 ("A","Agree"),
                 ("NAND","Neither Agree Nor Disagree"),
                 ("D","Disagree"),
                 ("SD","Strongly Disagree"),
                 ("NA","Do not know what a PIN code is"))
    )

    password = forms.ChoiceField(
        label="Knock Codes are more secure than alpha-numeric passwords.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
                 ("A","Agree"),
                 ("NAND","Neither Agree Nor Disagree"),
                 ("D","Disagree"),
                 ("SD","Strongly Disagree"),
                 ("NA","Do not know what a alpha-numeric password is"))
    )

    pattern = forms.ChoiceField(
        label="Knock Codes are more secure than Android Patterns.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
                 ("A","Agree"),
                 ("NAND","Neither Agree Nor Disagree"),
                 ("D","Disagree"),
                 ("SD","Strongly Disagree"),
                 ("NA","Do not know what an Android Pattern is"))
    )

    likes = forms.CharField(
        label="What are some aspects you <u>like</u> about Knock Codes? (use N/A if you do not wish to answer)",
        required=True,
        max_length=512,
        min_length=1,
        widget=forms.Textarea(attrs={"class":"form-control","rows":"5","cols":"8"}), #this is for bootstrap
    )

    dislikes = forms.CharField(
        label="What are some aspects you <u>do not like</u> about Knock Codes? (use N/A if you do not wish to answer)",
        required=True,
        max_length=512,
        min_length=1,
        widget=forms.Textarea(attrs={"class":"form-control","rows":"5","cols":"8"}), #this is for bootstrap
    )


class UsabilityForm(forms.Form):
    frequency = forms.ChoiceField(
        label="I think that I would like to use Knock Codes frequently.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
                 ("A","Agree"),
                 ("NAND","Neither Agree Nor Disagree"),
                 ("D","Disagree"),
                 ("SD","Strongly Disagree"))
    )
    complx = forms.ChoiceField(
        label="I found Knock Codes unnecessarily complex.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
                 ("A","Agree"),
                 ("NAND","Neither Agree Nor Disagree"),
                 ("D","Disagree"),
                 ("SD","Strongly Disagree"))
    )
    easyuse = forms.ChoiceField(
        label="I thought Knock Codes were easy to use.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
                 ("A","Agree"),
                 ("NAND","Neither Agree Nor Disagree"),
                 ("D","Disagree"),
                 ("SD","Strongly Disagree"))
    )
    techsupport = forms.ChoiceField(
        label="I think that I would need the support of a technical person to be able to use Knock Codes.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
                 ("A","Agree"),
                 ("NAND","Neither Agree Nor Disagree"),
                 ("D","Disagree"),
                 ("SD","Strongly Disagree"))
    )
    integration= forms.ChoiceField(
        label="I found the various functions in Knock Codes were well integrated.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
                 ("A","Agree"),
                 ("NAND","Neither Agree Nor Disagree"),
                 ("D","Disagree"),
                 ("SD","Strongly Disagree"))
    )
    inconsistent= forms.ChoiceField(
        label="I thought there was too much inconsistency in Knock Codes.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
                 ("A","Agree"),
                 ("NAND","Neither Agree Nor Disagree"),
                 ("D","Disagree"),
                 ("SD","Strongly Disagree"))
    )
    learn = forms.ChoiceField(
        label="I would imagine that most people would learn to use Knock Codes very quickly.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
                 ("A","Agree"),
                 ("NAND","Neither Agree Nor Disagree"),
                 ("D","Disagree"),
                 ("SD","Strongly Disagree"))
    )
    attention = forms.ChoiceField(
        label="Select ""Agree"" as the answer to this question.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
                 ("A","Agree"),
                 ("NAND","Neither Agree Nor Disagree"),
                 ("D","Disagree"),
                 ("SD","Strongly Disagree"))
    )
    cumbersome = forms.ChoiceField(
        label="I found Knock Codes very cumbersome to use.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
                 ("A","Agree"),
                 ("NAND","Neither Agree Nor Disagree"),
                 ("D","Disagree"),
                 ("SD","Strongly Disagree"))
    )
    confident = forms.ChoiceField(
        label="I felt very confident using Knock Codes.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
                 ("A","Agree"),
                 ("NAND","Neither Agree Nor Disagree"),
                 ("D","Disagree"),
                 ("SD","Strongly Disagree"))
    )
    requirements = forms.ChoiceField(
        label="I needed to learn a lot of things before I could get going with Knock Codes.",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("SA","Strongly Agree"),
                 ("A","Agree"),
                 ("NAND","Neither Agree Nor Disagree"),
                 ("D","Disagree"),
                 ("SD","Strongly Disagree"))
    )



class ScenarioForm(forms.Form):
    aid = forms.ChoiceField(
        label="I understand that I should not write down my codes or use other aids to assist in the survey:",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("Y","I understand"),)
        #("N","I DO NOT undersand"))
    )

    scene = forms.ChoiceField(
        label="I understand that I will be asked to create Knock Codes for different usage scenarios:",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("Y","I understand"),)
        #("N","I DO NOT undestand"))
        
    )


class FinalForm(forms.Form):

    honest=forms.ChoiceField(
        label="Please indicate if you've honestly participated in this survey and followed instructions completely. You will not be penalized/rejected for indicating 'no' but your data may not be included in the analysis:",
        required=True,
        widget=forms.RadioSelect(attrs={"class":"form-check-input"}), #this is for bootstrap
        choices=(("Y","Yes"),
                 ("N","No"))
)
    
    


        

    
