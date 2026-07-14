import io
import pypdf
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject

def create_textbook_pdf(output_path: str):
    writer = pypdf.PdfWriter()
    
    # 10 pages of textbook content
    pages_content = [
        # Page 1: Chapter 1: Introduction
        (
            "Chapter 1: Introduction to Computer Networks\n"
            "A computer network is a system of interconnected computers and devices that share resources and exchange data. "
            "Networks are classified by their geographic scale: Local Area Networks (LAN) span small areas like homes or offices, "
            "Wide Area Networks (WAN) cover large geographic areas such as countries or continents, and Metropolitan Area Networks "
            "(MAN) cover cities. Topologies describe network layouts: Star topology connects all nodes to a central hub, Ring connects "
            "nodes in a closed loop, and Mesh connects every node directly to multiple others for redundancy. Network protocols "
            "define standardized rules for data communication across systems."
        ),
        # Page 2: Chapter 2: The Physical Layer
        (
            "Chapter 2: The Physical Layer\n"
            "The physical layer is the lowest layer of the OSI model and deals with transmission of raw unstructured bit streams over "
            "a physical medium. Physical media include guided media like copper twisted-pair cables, coaxial cables, and fiber-optic cables, "
            "as well as unguided wireless media like radio waves, microwaves, and infrared. Bandwidth represents the maximum data transfer "
            "rate of a channel, measured in bits per second. Signaling techniques, such as amplitude, frequency, and phase modulation, "
            "translate digital binary data into physical signals suited for transmission over the communication media."
        ),
        # Page 3: Chapter 3: The Data Link Layer
        (
            "Chapter 3: The Data Link Layer\n"
            "The data link layer is responsible for error-free transfer of data frames between adjacent nodes over a physical link. "
            "It performs framing to package bit streams into discrete packets, error detection using checksums or Cyclic Redundancy Checks "
            "(CRC), and flow control to prevent a fast sender from overwhelming a slow receiver. Media Access Control (MAC) sublayer "
            "handles sharing of a common transmission medium among multiple stations. MAC addresses are unique hardware identifiers "
            "assigned to network interfaces for physical address resolution."
        ),
        # Page 4: Chapter 4: The Network Layer
        (
            "Chapter 4: The Network Layer\n"
            "The network layer manages host-to-host communication, routing packets across multiple interconnected networks. "
            "Routing algorithms determine the optimal path for packets to travel from source to destination: link-state routing "
            "(e.g., OSPF) maintains a complete map of the network, while distance-vector routing (e.g., RIP) updates paths based on "
            "neighbor tables. IP addressing (IPv4 and IPv6) provides logical, hierarchical identification for devices. IPv4 uses "
            "32-bit addresses, whereas IPv6 uses 128-bit addresses to resolve address exhaustion."
        ),
        # Page 5: Chapter 5: The Transport Layer
        (
            "Chapter 5: The Transport Layer\n"
            "The transport layer provides end-to-end communication services, ensuring reliable data transfer, flow control, and multiplexing. "
            "Transmission Control Protocol (TCP) is connection-oriented, providing reliable, ordered delivery with error checking, "
            "three-way handshakes, and congestion control algorithms. User Datagram Protocol (UDP) is connectionless, offering "
            "unreliable, fast delivery without flow control or ordering, making it ideal for real-time video streaming or gaming. "
            "Port numbers multiplex communication channels for different applications."
        ),
        # Page 6: Chapter 6: The Session Layer
        (
            "Chapter 6: The Session Layer\n"
            "The session layer manages sessions and dialogs between applications on different devices. "
            "It establishes, maintains, synchronizes, and terminates connections between local and remote applications. "
            "Key functions include dialog control, determining whether communication is simplex, half-duplex, or full-duplex, "
            "and token management to prevent simultaneous operations of critical actions. Synchronization points are inserted "
            "into the data stream to allow recovery in case of connection failure, preventing complete retransmission."
        ),
        # Page 7: Chapter 7: The Presentation Layer
        (
            "Chapter 7: The Presentation Layer\n"
            "The presentation layer acts as the data translator for the network, formatting data for application layer display. "
            "It is responsible for data translation between different syntax structures, such as ASCII, EBCDIC, or UTF-8, "
            "data encryption and decryption for secure communication, and data compression to optimize transmission bandwidth. "
            "Common formats managed at this layer include JSON, XML, JPEG, and MP3, shielding the application layer from hardware-specific "
            "data representation differences."
        ),
        # Page 8: Chapter 8: The Application Layer
        (
            "Chapter 8: The Application Layer\n"
            "The application layer is the highest layer and directly interacts with software applications to provide network services. "
            "Protocols at this layer include HTTP for web browsing, DNS for mapping domain names to IP addresses, SMTP and IMAP for "
            "email delivery, and FTP for file transfers. Modern applications integrate Retrieval-Augmented Generation (RAG) systems "
            "to query knowledge indexes built from textbook documents and return grounded answers, demonstrating interactive "
            "presentation layers connected to REST APIs."
        ),
        # Page 9: Chapter 9: Network Security
        (
            "Chapter 9: Network Security\n"
            "Network security involves protecting network infrastructure and data from unauthorized access, misuse, or alteration. "
            "Firewalls inspect incoming and outgoing traffic based on security rules to block threats. Cryptography provides "
            "confidentiality and integrity: symmetric encryption uses a single shared key, while asymmetric encryption uses a "
            "public-private key pair. Transport Layer Security (TLS) secures web traffic using asymmetric encryption for handshakes "
            "and symmetric encryption for data transfer."
        ),
        # Page 10: Chapter 10: Advanced Topics
        (
            "Chapter 10: Advanced Topics\n"
            "Advanced network architectures include Software-Defined Networking (SDN), which decouples the control plane from the "
            "forwarding plane for centralized control. Edge computing processes data closer to the source to reduce latency. "
            "Fifth-generation (5G) cellular networks offer high bandwidth, low latency, and support for massive Internet of Things "
            "(IoT) device deployments, transforming wireless communication capabilities and industrial automation."
        )
    ]
    
    font_dict = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica")
    })
    
    for idx, content in enumerate(pages_content):
        # Create a page
        page = writer.add_blank_page(width=612, height=792)  # Letter size
        
        # Add fonts
        page[NameObject("/Resources")] = DictionaryObject()
        resources: any = page[NameObject("/Resources")]
        resources[NameObject("/Font")] = DictionaryObject({
            NameObject("/F1"): font_dict
        })
        
        # Prepare text PDF operators
        # We need to escape parenthesis for PDF format
        title, body = content.split("\n", 1)
        escaped_title = title.replace("(", "\\(").replace(")", "\\)")
        
        # Chunk body into sentences/phrases to prevent long PDF strings overflowing the canvas
        # Since it's a mock PDF, we split by sentences
        sentences = body.split(". ")
        body_operators = []
        for s in sentences:
            if s.strip():
                escaped_s = s.strip().replace("(", "\\(").replace(")", "\\)") + "."
                # Move down 20 units and draw text
                body_operators.append(f"0 -24 Td\n({escaped_s}) Tj")
                
        joined_body = "\n".join(body_operators)
        
        stream_content = f"""BT
/F1 16 Tf
50 720 Td
({escaped_title}) Tj
/F1 11 Tf
{joined_body}
ET""".encode("utf-8")

        contents_stream = DecodedStreamObject()
        contents_stream._data = stream_content
        page[NameObject("/Contents")] = contents_stream

    writer.add_metadata({
        "/Title": "Computer Networks: Foundations and Protocols",
        "/Author": "Dr. Alice Smith",
        "/Subject": "Computer Science - Network Architectures",
        "/Creator": "Textbook Generator",
        "/Producer": "Report Generator v1.0"
    })
    
    with open(output_path, "wb") as f:
        writer.write(f)

if __name__ == "__main__":
    create_textbook_pdf("computer_networks.pdf")
    print("Generated computer_networks.pdf successfully.")
