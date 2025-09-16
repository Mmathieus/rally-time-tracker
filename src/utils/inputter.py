from prompt_toolkit import prompt as prmnt
from prompt_toolkit.completion import WordCompleter


def get_user_input(symbol='◇', prompt="Select an option", with_colon=True, lowercase=True, autocomplete_options=None) -> str:
    final_prompt = f"{symbol} {prompt}{':' if with_colon else ''} "
    
    # try:
    if autocomplete_options:
        completer = WordCompleter(autocomplete_options, ignore_case=True)
        user_input = prmnt(message=final_prompt, completer=completer, complete_while_typing=True).strip()
    else:
        user_input = input(final_prompt).strip()
        
    if lowercase:
        return user_input.lower()
    return user_input
