import streamlit as st

# Set up the page configuration
st.set_page_config(page_title="DES Calculator", layout="wide")

# -------------------------------
# Utility Functions for Bit Handling
# -------------------------------
def text_to_bin(text):
    """Convert a plain text string to a binary string (8 bits per character)."""
    return ''.join(format(ord(c), '08b') for c in text)

def bin_to_hex(bin_str):
    """Convert a binary string to a hexadecimal string."""
    hex_str = hex(int(bin_str, 2))[2:].upper()
    return hex_str.zfill(len(bin_str) // 4)

def permute(input_bits, table):
    """Permute input_bits according to the given table (1-indexed)."""
    return ''.join(input_bits[i - 1] for i in table)

# -------------------------------
# DES Tables
# -------------------------------
# Initial Permutation (IP) and Final Permutation (FP)
IP_table = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]

FP_table = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25
]

# Expansion table (E) – expands 32 bits to 48 bits
E_table = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1
]

# S-boxes (8 boxes)
S_boxes = [
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
    ],
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
    ],
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]
    ],
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]
    ],
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
    ],
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
    ],
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
    ],
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
    ]
]

# Permutation P (32-bit)
P_table = [
    16, 7, 20, 21, 29, 12, 28, 17,
    1, 15, 23, 26, 5, 18, 31, 10,
    2, 8, 24, 14, 32, 27, 3, 9,
    19, 13, 30, 6, 22, 11, 4, 25
]

# Key schedule tables: PC-1 and PC-2
PC1_table = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4
]

PC2_table = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]

# Number of left shifts per round (for key schedule)
shift_table = [1, 1, 2, 2, 2, 2, 2, 2,
               1, 2, 2, 2, 2, 2, 2, 1]

# -------------------------------
# Key Generation Function
# -------------------------------
def generate_round_keys(key):
    """Generate 16 round keys (48 bits each) from the 64-bit key."""
    key_permuted = permute(key, PC1_table)  # 56 bits
    C = key_permuted[:28]
    D = key_permuted[28:]
    round_keys = []
    for shift in shift_table:
        C = C[shift:] + C[:shift]
        D = D[shift:] + D[:shift]
        combined = C + D
        round_key = permute(combined, PC2_table)
        round_keys.append(round_key)
    return round_keys

# -------------------------------
# DES Round Function (f)
# -------------------------------
def DES_round(R, round_key):
    """
    DES round function:
      1. Expand R (32 bits) to 48 bits.
      2. XOR with the round key.
      3. Process through 8 S-boxes.
      4. Permute the 32-bit output.
    """
    R_expanded = permute(R, E_table)
    xor_result = ''.join('0' if a == b else '1' for a, b in zip(R_expanded, round_key))
    blocks = [xor_result[i*6:(i+1)*6] for i in range(8)]
    sbox_output = ""
    for i, block in enumerate(blocks):
        row = int(block[0] + block[5], 2)
        col = int(block[1:5], 2)
        s_val = S_boxes[i][row][col]
        sbox_output += format(s_val, '04b')
    f_out = permute(sbox_output, P_table)
    return R_expanded, xor_result, blocks, sbox_output, f_out

# -------------------------------
# DES Encryption Function (with Step-by-Step Logging)
# -------------------------------
def DES_encrypt(plaintext, key):
    steps = []
    plaintext_bin = text_to_bin(plaintext)
    key_bin = text_to_bin(key)
    
    steps.append(f"Plaintext (text): {plaintext}")
    steps.append(f"Plaintext (bin): {plaintext_bin}")
    steps.append(f"Key (text): {key}")
    steps.append(f"Key (bin): {key_bin}")
    
    # 1. Initial Permutation (IP)
    IP = permute(plaintext_bin, IP_table)
    steps.append(f"After Initial Permutation (IP): {IP}")
    
    # 2. Split into Left and Right
    L = IP[:32]
    R = IP[32:]
    steps.append(f"L0: {L}")
    steps.append(f"R0: {R}")
    
    # 3. Generate 16 Round Keys
    round_keys = generate_round_keys(key_bin)
    
    # 4. 16 Rounds
    for i in range(16):
        steps.append(f"----- Round {i+1} -----")
        steps.append(f"Round Key: {round_keys[i]}")
        R_expanded, xor_result, blocks, sbox_out, f_out = DES_round(R, round_keys[i])
        steps.append(f"Expanded R (48 bits): {R_expanded}")
        steps.append(f"R XOR Key: {xor_result}")
        for j, block in enumerate(blocks):
            steps.append(f"  S-box {j+1} input: {block}")
        steps.append(f"After S-box substitution: {sbox_out}")
        steps.append(f"After Permutation (P-box): {f_out}")
        new_R = ''.join('0' if a == b else '1' for a, b in zip(L, f_out))
        steps.append(f"New R (L XOR f(R,Key)): {new_R}")
        L = R
        R = new_R
        steps.append(f"New L: {L}")
        steps.append(f"New R: {R}")
    
    # 5. Preoutput and Final Permutation
    combined = R + L
    steps.append(f"Combined (R16 + L16): {combined}")
    cipher_bin = permute(combined, FP_table)
    steps.append(f"After Final Permutation (FP): {cipher_bin}")
    
    cipher_hex = bin_to_hex(cipher_bin)
    steps.append(f"Ciphertext (hex): {cipher_hex}")
    
    return steps, cipher_hex

# -------------------------------
# Streamlit App Layout
# -------------------------------
def main():
    st.title("DES Algorithm Calculator")
    st.markdown("### Step-by-Step DES Encryption")
    
    # Sidebar instructions
    with st.sidebar:
        st.header("Instructions")
        st.info(
            "1. **Input Requirements:**\n"
            "   - Plaintext: 8 ASCII characters\n"
            "   - Key: 8 ASCII characters\n\n"
            "2. The app converts inputs to binary and performs DES encryption.\n"
            "3. Detailed steps are available in the 'Encryption Details' section below."
        )
    
    # Input Section
    col1, col2 = st.columns(2)
    with col1:
        plaintext = st.text_input("Plaintext (8 characters)", "DESdemo!")
    with col2:
        key = st.text_input("Key (8 characters)", "mykey123")
    
    # Encrypt button
    if st.button("Encrypt"):
        if len(plaintext) != 8 or len(key) != 8:
            st.error("Both plaintext and key must be exactly 8 characters long.")
        else:
            steps, cipher_hex = DES_encrypt(plaintext, key)
            st.success(f"Final Ciphertext (hex): {cipher_hex}")
            
            # Expandable section for step-by-step details
            with st.expander("Show Encryption Details"):
                for step in steps:
                    st.write(step)

if __name__ == '__main__':
    main()
