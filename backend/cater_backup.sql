--
-- PostgreSQL database dump
--

\restrict pnELq9DrVQcLI3i9Ox0u6MYseIzR1YkumVRTQZPiguRQOFqqQRFx5BPphZW7bcZ

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: contact_inquiries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contact_inquiries (
    inquiry_id integer NOT NULL,
    name character varying(100),
    phone character varying(20),
    email character varying(100),
    message text,
    inquiry_date timestamp without time zone,
    status character varying(20)
);


ALTER TABLE public.contact_inquiries OWNER TO postgres;

--
-- Name: contact_inquiries_inquiry_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.contact_inquiries_inquiry_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.contact_inquiries_inquiry_id_seq OWNER TO postgres;

--
-- Name: contact_inquiries_inquiry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.contact_inquiries_inquiry_id_seq OWNED BY public.contact_inquiries.inquiry_id;


--
-- Name: customers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers (
    customer_id integer NOT NULL,
    full_name character varying(100) NOT NULL,
    phone_number character varying(20) NOT NULL,
    email character varying(100),
    password_hash character varying(255),
    created_at timestamp without time zone,
    total_orders_count integer
);


ALTER TABLE public.customers OWNER TO postgres;

--
-- Name: customers_customer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customers_customer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customers_customer_id_seq OWNER TO postgres;

--
-- Name: customers_customer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customers_customer_id_seq OWNED BY public.customers.customer_id;


--
-- Name: event_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_types (
    event_type_id integer NOT NULL,
    event_name character varying(50),
    minimum_guests integer,
    description character varying(255),
    icon_url character varying(255),
    image_url character varying(255),
    is_active boolean
);


ALTER TABLE public.event_types OWNER TO postgres;

--
-- Name: event_types_event_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.event_types_event_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.event_types_event_type_id_seq OWNER TO postgres;

--
-- Name: event_types_event_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.event_types_event_type_id_seq OWNED BY public.event_types.event_type_id;


--
-- Name: menu_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.menu_items (
    item_id integer NOT NULL,
    item_name character varying(100) NOT NULL,
    category character varying(50),
    price_per_plate double precision,
    is_vegetarian boolean,
    image_url character varying(255),
    description character varying(255),
    total_orders_count integer,
    is_available boolean,
    stock_quantity integer,
    created_at timestamp without time zone
);


ALTER TABLE public.menu_items OWNER TO postgres;

--
-- Name: menu_items_item_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.menu_items_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.menu_items_item_id_seq OWNER TO postgres;

--
-- Name: menu_items_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.menu_items_item_id_seq OWNED BY public.menu_items.item_id;


--
-- Name: monthly_statistics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.monthly_statistics (
    stat_id integer NOT NULL,
    year integer,
    month integer,
    total_orders integer,
    total_revenue double precision,
    confirmed_orders integer,
    pending_orders integer,
    completed_orders integer,
    cancelled_orders integer
);


ALTER TABLE public.monthly_statistics OWNER TO postgres;

--
-- Name: monthly_statistics_stat_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.monthly_statistics_stat_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.monthly_statistics_stat_id_seq OWNER TO postgres;

--
-- Name: monthly_statistics_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.monthly_statistics_stat_id_seq OWNED BY public.monthly_statistics.stat_id;


--
-- Name: order_menu_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_menu_items (
    order_menu_id integer NOT NULL,
    order_id integer,
    menu_item_id integer,
    quantity integer,
    price_at_order_time double precision
);


ALTER TABLE public.order_menu_items OWNER TO postgres;

--
-- Name: order_menu_items_order_menu_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_menu_items_order_menu_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_menu_items_order_menu_id_seq OWNER TO postgres;

--
-- Name: order_menu_items_order_menu_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_menu_items_order_menu_id_seq OWNED BY public.order_menu_items.order_menu_id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    order_id integer NOT NULL,
    customer_id integer,
    customer_name character varying(100),
    phone_number character varying(20),
    email character varying(100),
    event_type character varying(50),
    number_of_guests integer,
    event_date character varying(20),
    event_time character varying(20),
    venue_address text,
    special_requirements text,
    status character varying(20),
    total_amount double precision,
    razorpay_order_id character varying(100),
    payment_method character varying(20),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- Name: orders_order_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orders_order_id_seq OWNER TO postgres;

--
-- Name: orders_order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_order_id_seq OWNED BY public.orders.order_id;


--
-- Name: contact_inquiries inquiry_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contact_inquiries ALTER COLUMN inquiry_id SET DEFAULT nextval('public.contact_inquiries_inquiry_id_seq'::regclass);


--
-- Name: customers customer_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers ALTER COLUMN customer_id SET DEFAULT nextval('public.customers_customer_id_seq'::regclass);


--
-- Name: event_types event_type_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_types ALTER COLUMN event_type_id SET DEFAULT nextval('public.event_types_event_type_id_seq'::regclass);


--
-- Name: menu_items item_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_items ALTER COLUMN item_id SET DEFAULT nextval('public.menu_items_item_id_seq'::regclass);


--
-- Name: monthly_statistics stat_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_statistics ALTER COLUMN stat_id SET DEFAULT nextval('public.monthly_statistics_stat_id_seq'::regclass);


--
-- Name: order_menu_items order_menu_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_menu_items ALTER COLUMN order_menu_id SET DEFAULT nextval('public.order_menu_items_order_menu_id_seq'::regclass);


--
-- Name: orders order_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders ALTER COLUMN order_id SET DEFAULT nextval('public.orders_order_id_seq'::regclass);


--
-- Data for Name: contact_inquiries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.contact_inquiries (inquiry_id, name, phone, email, message, inquiry_date, status) FROM stdin;
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customers (customer_id, full_name, phone_number, email, password_hash, created_at, total_orders_count) FROM stdin;
11	Test User	1234567890	test@test.com	\N	2025-12-28 09:52:50.135773	0
12	Test User	1234567890	test2@test.com	\N	2025-12-28 09:54:09.116977	1
10	Balaji	9876543210	ankibalaji@gmail.com	\N	2025-12-28 09:48:48.319788	5
13	Sathish	9655968666	sathish@gmail.com	\N	2025-12-28 16:29:29.04424	1
14	Karthik	6987624652	karthik@gmail.com	\N	2025-12-28 17:20:06.098653	2
7	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	\N	2025-12-23 20:38:51.157823	14
15	Rahul	9655968666	rahul@gmail.com	\N	2025-12-29 18:51:02.226271	1
1	Rajesh Kumar	9876543210	rajesh@example.com	pbkdf2:sha256:600000$do86BlJikWgruW6c$e2319a576aeee49114749af59bb4cac6fc117e6a26fb7dd60af2cb6015321019	2025-12-23 19:34:19.20437	0
2	Priya Sharma	9876543211	priya@example.com	pbkdf2:sha256:600000$oGG2pSLaDJw2onKG$0cfb3965c3c4e7c1f8794fba26f7b7fe25a69328100e30c61833f642086bcb0b	2025-12-23 19:34:19.204387	0
3	Amit Patel	9876543212	amit@example.com	pbkdf2:sha256:600000$F1iIqpqdgKiQNO2p$6646b4cf9f8aacd27b759c4cc67db9d60ed33fa1d338da5b8b949028175f16a2	2025-12-23 19:34:19.20439	0
4	Sneha Reddy	9876543213	sneha@example.com	\N	2025-12-23 19:34:19.204393	0
5	Vikram Singh	9876543214	vikram@example.com	pbkdf2:sha256:600000$EaD2Zg0ProiAeHiZ$c19c868e0e31b95503fe6545bfb97e3c4369113c2bb49716ea5a4b30ff153138	2025-12-23 19:34:19.204396	0
6	Test User	9999999999	test@example.com	\N	2025-12-23 20:10:30.546994	1
8	Nandha Gopal	9571546882	nandhagopal@gmail.com	\N	2025-12-27 13:43:14.906193	1
9	Hari	6984175724	harinadar@gmail.com	\N	2025-12-27 17:45:53.172397	1
\.


--
-- Data for Name: event_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_types (event_type_id, event_name, minimum_guests, description, icon_url, image_url, is_active) FROM stdin;
1	Wedding	50	Full wedding catering package	\N	https://example.com/wedding.jpg	t
2	Birthday	10	Birthday parties and small events	\N	https://example.com/birthday.jpg	t
\.


--
-- Data for Name: menu_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.menu_items (item_id, item_name, category, price_per_plate, is_vegetarian, image_url, description, total_orders_count, is_available, stock_quantity, created_at) FROM stdin;
1	Veg Meals	main	120	t	/images/meals_veg.png	South Indian rice platter with curries and sides.	0	t	58	2025-12-28 08:52:25.109328
11	Semiya Payasam	Desserts	60	t	/static/uploads/Semiya_payasam.jpg	Delicious Semiya Payasam for our lovely customers...	0	t	63	2025-12-28 10:18:25.044759
15	Panner Fried Rice	Main Course	85	t	http://127.0.0.1:5000/static/uploads/paneer_fried_rice_1.jpg	Delicious Panner Fried Rice	0	t	100	2025-12-29 18:53:14.97086
6	Paneer Tikka	starter	110	t	/images/paneer-tikka.jpg	Smoky marinated paneer skewers.	0	t	80	2025-12-28 08:52:25.109328
3	Chole Puri	main	100	t	/images/chola_puri.png	Spiced chickpeas served with fluffy puris.	0	t	0	2025-12-28 08:52:25.109328
2	Paneer Butter Masala	main	100	t	/images/panner_butter_masala.png	Creamy paneer cooked with butter and spices.	0	t	99	2025-12-28 08:52:25.109328
12	Mushroom gravy	Main Course	80	t	/static/uploads/mushroom_gravy.jpg	Delicious mushroom gravy....	0	t	100	2025-12-29 16:10:49.337634
4	Dal Makhani	main	85	t	/images/dhal_makini.png	Slow-cooked black lentils finished with cream.	0	t	100	2025-12-28 08:52:25.109328
5	Veg Biryani	main	120	t	/images/veg-biriyani.webp	Aromatic basmati rice with mixed vegetables.	0	t	44	2025-12-28 08:52:25.109328
7	Veg Cutlet	starter	90	t	/images/veg-cutlet.webp	Crispy vegetable patties with herbs.	0	t	100	2025-12-28 08:52:25.109328
8	Gulab Jamun	dessert	80	t	/images/gulab-jamun.jpg	Soft milk dumplings soaked in syrup.	0	t	100	2025-12-28 08:52:25.109328
9	Rasmalai	dessert	90	t	/images/rasamalai.webp	Cottage cheese patties in saffron milk.	0	t	100	2025-12-28 08:52:25.109328
\.


--
-- Data for Name: monthly_statistics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.monthly_statistics (stat_id, year, month, total_orders, total_revenue, confirmed_orders, pending_orders, completed_orders, cancelled_orders) FROM stdin;
\.


--
-- Data for Name: order_menu_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_menu_items (order_menu_id, order_id, menu_item_id, quantity, price_at_order_time) FROM stdin;
1	1	2	1	180
2	1	3	1	100
3	2	1	1	120
4	2	2	1	180
5	2	3	1	100
6	2	4	1	150
7	3	2	1	180
8	3	3	1	100
9	3	4	1	150
10	4	1	1	500
11	5	2	1	180
12	5	4	1	150
13	5	8	1	100
14	6	2	1	180
15	6	3	1	100
16	6	8	1	100
17	7	6	1	170
18	7	8	1	100
19	8	1	1	120
20	8	3	1	100
21	9	1	1	120
22	9	3	1	100
23	10	1	1	120
24	10	3	1	100
25	11	1	1	120
26	11	3	1	100
27	12	1	1	120
28	12	5	1	80
29	13	3	1	100
30	14	3	1	140
31	14	5	1	100
34	16	3	1	140
35	16	5	1	100
36	17	7	1	130
37	18	7	1	130
38	19	7	1	130
40	21	1	1	120
41	21	5	1	100
46	24	5	1	100
49	26	3	1	140
50	27	1	1	123.45
51	28	3	1	140
52	29	3	1	140
53	30	5	1	100
56	32	3	1	140
57	33	5	1	100
58	34	5	1	100
59	34	7	1	130
60	38	1	2	75
61	39	1	1	120
62	40	1	1	120
63	41	1	1	120
64	42	11	1	60
66	44	2	1	140
67	45	1	1	120
69	46	3	50	180
70	47	3	50	180
74	49	1	15	120
75	49	5	15	150
76	49	11	15	60
77	50	1	20	120
78	50	5	20	150
79	50	11	20	60
81	52	5	1	150
82	53	5	20	150
83	53	6	20	110
65	43	\N	1	100
68	45	\N	1	100
80	51	\N	1	100
84	54	1	1	120
85	54	11	1	60
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (order_id, customer_id, customer_name, phone_number, email, event_type, number_of_guests, event_date, event_time, venue_address, special_requirements, status, total_amount, razorpay_order_id, payment_method, created_at, updated_at) FROM stdin;
35	10	Balaji	9876543210	ankibalaji@gmail.com	Delivery	1	2025-12-28	3:18:48 PM	Nanganallur, Chennai	\N	Pending	157.5	\N	online	2025-12-28 09:48:48.324386	\N
37	11	Test User	1234567890	test@test.com	Delivery	1	2025-12-28	15:00:00	123 Test St	\N	Pending	150	\N	cod	2025-12-28 09:52:50.135773	\N
39	10	Balaji	9657824962	ankibalaji@gmail.com	Delivery	1	2025-12-28	3:25:15 PM	Chennai	\N	Pending	126	order_RwzPGrLTohJTjc	online	2025-12-28 09:55:15.132624	2025-12-28 09:55:17.329424
42	7	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-28	3:53:17 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	63	\N	cod	2025-12-28 10:23:17.779356	\N
51	7	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-28	11:11:59 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	105	\N	cod	2025-12-28 17:41:59.833533	\N
52	7	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-29	9:24:15 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Paid	157.5	order_RxU3fcKruUGI6m	online	2025-12-29 15:54:15.991303	2025-12-29 15:54:44.953271
36	10	Balaji	9876543210	ankibalaji@gmail.com	Delivery	1	2025-12-28	3:19:23 PM	Nanganallur, Chennai	\N	Pending	157.5	\N	cod	2025-12-28 09:49:24.059302	\N
38	12	Test User	1234567890	test2@test.com	Delivery	1	2025-12-28	15:00:00	123 Test St	\N	Pending	150	\N	cod	2025-12-28 09:54:09.116977	\N
32	7	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-26	6:53:38 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Paid	147	order_RwFtCXiRh0dEn0	online	2025-12-26 13:23:39.074036	2025-12-26 13:24:31.691688
33	8	Nandha Gopal	9571546882	nandhagopal@gmail.com	Delivery	1	2025-12-27	7:13:14 PM	Anna nagar, chennai	\N	Paid	105	\N	cod	2025-12-27 13:43:14.91945	2025-12-27 13:44:38.970992
34	9	Hari	6984175724	harinadar@gmail.com	Delivery	1	2025-12-27	11:15:53 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	241.5	\N	cod	2025-12-27 17:45:53.600385	\N
44	7	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-28	9:08:45 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	147	order_Rx5G8gnz8nHGUz	online	2025-12-28 15:38:45.702862	2025-12-28 15:38:48.31798
48	7	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Bulk Order	20	2025-12-28	10:40:04 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	7980	\N	online	2025-12-28 17:10:05.135383	\N
50	14	Karthik	9874854575	karthik@gmail.com	Bulk Order	20	2025-12-28	10:58:17 PM	Chennai	\N	Paid	6930	order_Rx77p6mvo2boZl	online	2025-12-28 17:28:17.382923	2025-12-28 17:28:56.04039
53	7	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Bulk Order	20	2025-12-29	9:33:42 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Paid	5460	order_RxUDcMXjd6IHLq	online	2025-12-29 16:03:42.13311	2025-12-29 16:04:11.673976
1	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-10	8:07:13 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Paid	294	\N	online	2025-12-10 14:37:14.425347	2025-12-24 17:34:06.149323
2	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-10	8:10:01 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Cancelled	577.5	\N	online	2025-12-10 14:40:01.999776	2025-12-24 18:43:54.576673
3	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-10	8:10:39 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Out for Delivery	451.5	\N	online	2025-12-10 14:40:40.253876	2025-12-24 10:25:30.693096
4	\N	Test User	9999999999	test@example.com	Delivery	5	2025-12-11	23:30	123 Test St	\N	Paid	500	\N	online	2025-12-11 18:02:12.236968	2025-12-24 10:10:06.442269
40	10	Balaji	9657824962	ankibalaji@gmail.com	Delivery	1	2025-12-28	3:29:02 PM	Chennai	\N	Pending	126	order_RwzTGbz2wa069z	online	2025-12-28 09:59:02.309321	2025-12-28 09:59:04.330169
45	13	Sathish	9655968666	sathish@gmail.com	Delivery	1	2025-12-28	9:59:28 PM	\nChennai	\N	Paid	231	order_Rx67ifw6LfLTks	online	2025-12-28 16:29:29.050185	2025-12-28 16:30:06.582003
46	7	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Bulk Order	50	2025-12-28	10:38:23 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	9450	order_Rx6mqTB4lZMWSd	online	2025-12-28 17:08:23.915443	2025-12-28 17:08:27.609717
47	7	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Bulk Order	50	2025-12-28	10:38:49 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	9450	\N	cod	2025-12-28 17:08:49.27047	\N
54	15	Rahul	9655968666	rahul@gmail.com	Delivery	1	2025-12-29	12:21:02 AM	Chennai	\N	Paid	189	\N	cod	2025-12-29 18:51:02.595823	2025-12-29 18:51:59.585003
5	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-11	11:33:51 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	451.5	\N	online	2025-12-11 18:03:52.444815	\N
41	10	Balaji	9657824962	ankibalaji@gmail.com	Delivery	1	2025-12-28	3:37:24 PM	Chennai	\N	Paid	126	order_Rwzc6QwkTpUuLx	online	2025-12-28 10:07:25.055831	2025-12-28 10:09:00.735115
43	7	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-28	3:56:07 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	105	\N	cod	2025-12-28 10:26:07.078009	\N
49	14	Karthik	6987624652	karthik@gmail.com	Bulk Order	15	2025-12-28	10:50:06 PM	Chennai	\N	Pending	5197.5	order_Rx6zAliBdxJpN5	online	2025-12-28 17:20:06.105654	2025-12-28 17:20:07.798083
6	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-13	6:17:14 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	399	\N	online	2025-12-13 12:47:15.084125	\N
7	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-15	11:03:19 AM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	283.5	\N	online	2025-12-15 05:33:20.486273	\N
8	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-15	1:13:15 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	231	order_RroDHqO7VoS00O	online	2025-12-15 07:43:15.882474	2025-12-15 07:43:18.927548
9	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-15	1:13:17 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	231	order_RroDIW4772Z7ah	online	2025-12-15 07:43:17.106702	2025-12-15 07:43:19.541388
10	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-15	1:13:18 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	231	order_RroDJS8QkRlgz0	online	2025-12-15 07:43:19.15554	2025-12-15 07:43:20.391952
11	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-15	1:13:18 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	231	order_RroDJlXReyKvrM	online	2025-12-15 07:43:19.400601	2025-12-15 07:43:20.869872
12	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-15	1:15:44 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	210	order_RroFsqG67Wo03K	online	2025-12-15 07:45:45.395504	2025-12-15 07:45:46.40497
13	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-15	1:19:54 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	105	order_RroKHwrnJJodk2	online	2025-12-15 07:49:55.314372	2025-12-15 07:49:56.60144
14	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-15	12:37:30 AM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	252	order_Rrzs5yzIScmOgB	online	2025-12-15 19:07:31.033357	2025-12-15 19:07:34.965838
15	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-15	12:40:40 AM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	210	\N	online	2025-12-15 19:10:41.062734	\N
16	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-15	12:44:34 AM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	252	\N	online	2025-12-15 19:14:35.5286	\N
17	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-15	1:10:13 AM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	136.5	\N	online	2025-12-15 19:40:13.602188	\N
18	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-15	1:10:21 AM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	136.5	order_Rs0QmViF2Oi4wh	online	2025-12-15 19:40:22.236101	2025-12-15 19:40:25.116342
19	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-15	1:10:23 AM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	136.5	order_Rs0QpGtUnoRfAE	online	2025-12-15 19:40:23.996168	2025-12-15 19:40:27.635007
20	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-19	10:46:40 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	115.5	\N	online	2025-12-19 17:16:41.580625	\N
21	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-23	6:57:07 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	231	order_Rv4LUtd3IDK4PI	online	2025-12-23 13:27:07.820654	2025-12-23 13:27:10.883996
22	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-23	6:58:52 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	210	\N	cod	2025-12-23 13:28:52.727409	\N
23	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-23	11:14:05 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	178.5	\N	cod	2025-12-23 17:44:05.776856	\N
24	\N	Karthik	9876543210	karthik@gmail.com	Delivery	1	2025-12-23	11:25:52 PM	chennai	\N	Pending	220.5	\N	cod	2025-12-23 17:55:52.898262	\N
25	\N	Karthik	8270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-23	11:26:24 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Paid	84	order_Rv8vxDecsZ2vWw	online	2025-12-23 17:56:24.73777	2025-12-23 17:58:08.659972
26	\N	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-23	11:32:03 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Preparing	147	\N	cod	2025-12-23 18:02:03.800104	2025-12-24 09:29:28.36394
27	6	Test User	9999999999	test@example.com	Delivery	1	2025-12-24	10:00	Somewhere	\N	Paid	123.45	\N	cod	2025-12-23 20:10:30.558744	2025-12-24 09:16:34.155976
28	7	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-23	2:08:51 AM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Paid	147	\N	cod	2025-12-23 20:38:51.169438	2025-12-24 09:14:59.668099
29	7	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-23	2:09:18 AM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	147	order_RvBi0iFcQWKiNb	online	2025-12-23 20:39:18.586402	2025-12-24 09:34:17.438894
30	7	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-24	11:02:51 PM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	105	\N	cod	2025-12-24 17:32:52.310613	\N
31	7	Vianney Infant Raj. A	08270737274	sec23cs171@sairamtap.edu.in	Delivery	1	2025-12-24	12:11:26 AM	Sai leo nagar, poonthandalam village, West Tambaram , chennai - 600044	\N	Pending	210	\N	cod	2025-12-24 18:41:26.303304	\N
\.


--
-- Name: contact_inquiries_inquiry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.contact_inquiries_inquiry_id_seq', 1, false);


--
-- Name: customers_customer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.customers_customer_id_seq', 15, true);


--
-- Name: event_types_event_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_types_event_type_id_seq', 2, true);


--
-- Name: menu_items_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.menu_items_item_id_seq', 15, true);


--
-- Name: monthly_statistics_stat_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.monthly_statistics_stat_id_seq', 1, false);


--
-- Name: order_menu_items_order_menu_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.order_menu_items_order_menu_id_seq', 85, true);


--
-- Name: orders_order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.orders_order_id_seq', 54, true);


--
-- Name: contact_inquiries contact_inquiries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contact_inquiries
    ADD CONSTRAINT contact_inquiries_pkey PRIMARY KEY (inquiry_id);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (customer_id);


--
-- Name: event_types event_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_types
    ADD CONSTRAINT event_types_pkey PRIMARY KEY (event_type_id);


--
-- Name: menu_items menu_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.menu_items
    ADD CONSTRAINT menu_items_pkey PRIMARY KEY (item_id);


--
-- Name: monthly_statistics monthly_statistics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_statistics
    ADD CONSTRAINT monthly_statistics_pkey PRIMARY KEY (stat_id);


--
-- Name: order_menu_items order_menu_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_menu_items
    ADD CONSTRAINT order_menu_items_pkey PRIMARY KEY (order_menu_id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (order_id);


--
-- Name: order_menu_items order_menu_items_menu_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_menu_items
    ADD CONSTRAINT order_menu_items_menu_item_id_fkey FOREIGN KEY (menu_item_id) REFERENCES public.menu_items(item_id);


--
-- Name: order_menu_items order_menu_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_menu_items
    ADD CONSTRAINT order_menu_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id);


--
-- Name: orders orders_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(customer_id);


--
-- PostgreSQL database dump complete
--

\unrestrict pnELq9DrVQcLI3i9Ox0u6MYseIzR1YkumVRTQZPiguRQOFqqQRFx5BPphZW7bcZ

