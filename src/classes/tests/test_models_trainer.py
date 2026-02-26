import pytest
from src.classes.models import Trainer

pytestmark = pytest.mark.unit

def test_trainer_display_name_normal():
    trainer = Trainer(first_name="John", last_name="Doe")
    assert trainer.display_name == "John Doe"

def test_trainer_display_name_blank_first_name():
    trainer = Trainer(first_name="", last_name="Smith")
    assert trainer.display_name == "Smith"

def test_trainer_display_name_both_blank():
    trainer = Trainer(first_name="", last_name="")
    assert trainer.display_name == "TBA"

def test_trainer_display_name_template_injection_start():
    trainer = Trainer(first_name="{{exploit}}", last_name="Test")
    assert trainer.display_name == "TBA"

def test_trainer_display_name_template_injection_end():
    trainer = Trainer(first_name="Test", last_name="}}")
    assert trainer.display_name == "TBA"

def test_trainer_display_name_whitespace():
    trainer = Trainer(first_name="  ", last_name="  ")
    assert trainer.display_name == "TBA"

def test_trainer_display_initial_normal():
    trainer = Trainer(first_name="John")
    assert trainer.display_initial == "J"

def test_trainer_display_initial_lowercase():
    trainer = Trainer(first_name="alice")
    assert trainer.display_initial == "A"

def test_trainer_display_initial_numeric():
    trainer = Trainer(first_name="123")
    assert trainer.display_initial == "T"

def test_trainer_display_initial_empty():
    trainer = Trainer(first_name="")
    assert trainer.display_initial == "T"

def test_trainer_display_initial_whitespace():
    trainer = Trainer(first_name="  ")
    assert trainer.display_initial == "T"

def test_trainer_display_initial_special_char():
    trainer = Trainer(first_name="@user")
    assert trainer.display_initial == "T"

def test_trainer_str():
    trainer = Trainer(first_name="Jane", last_name="Smith")
    assert str(trainer) == "Jane Smith"
