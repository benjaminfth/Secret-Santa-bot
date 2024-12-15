import random
from protonmail import Client

# Function to assign Secret Santa pairs
def secret_santa(participants):
    givers = participants[:]
    receivers = participants[:]
    
    random.shuffle(receivers)
    
    for i in range(len(givers)):
        while givers[i] == receivers[i]:
            random.shuffle(receivers)
    
    return {givers[i]: receivers[i] for i in range(len(givers))}

# Function to send emails via ProtonMail
def send_email(sender_email, sender_password, recipient_email, giver, receiver):
    subject = "Your Secret Santa Assignment"
    body = f"Hi {giver},\n\nYou are the Secret Santa for {receiver}!\n\nHappy gifting!\n\nBest,\nSecret Santa Organizer"
    
    try:
        # Initialize ProtonMail client
        client = Client(sender_email, sender_password)
        client.login()
        
        # Send email
        client.send_message(
            to=recipient_email,
            subject=subject,
            body=body,
        )
        client.logout()
        print(f"Email successfully sent to {giver} ({recipient_email}).")
        return True
    except Exception as e:
        print(f"Failed to send email to {giver} ({recipient_email}): {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Replace these with your ProtonMail credentials
    sender_email = "your_protonmail@example.com"
    sender_password = "your_protonmail_password"

    # Participants list (name, email)
    participants = [
        ("Alice", "alice@example.com"),
        ("Bob", "bob@example.com"),
        ("Charlie", "charlie@example.com"),
        ("Diana", "diana@example.com")
    ]

    # Generate Secret Santa pairs
    matches = secret_santa([name for name, email in participants])
    print("Secret Santa Matches:")
    for giver, receiver in matches.items():
        print(f"{giver} -> {receiver}")

    # Send emails to participants
    for giver, receiver in matches.items():
        giver_email = next(email for name, email in participants if name == giver)
        send_email(sender_email, sender_password, giver_email, giver, receiver)
